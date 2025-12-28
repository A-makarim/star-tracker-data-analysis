import rawpy
import numpy as np
import matplotlib.pyplot as plt
from photutils.background import Background2D, MedianBackground
from photutils.detection import DAOStarFinder
from astropy.stats import SigmaClip, sigma_clipped_stats
from skimage.restoration import denoise_wavelet
import imageio.v3 as imageio

def main():
    image_path = 'IMG_1085.CR2'
    print(f"Loading image: {image_path}")
    
    try:
        with rawpy.imread(image_path) as raw:
            # postprocess() yields an 8-bit RGB image by default
            rgb = raw.postprocess()
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Convert to grayscale (0-255 range)
    print("Converting to grayscale...")
    gray = np.mean(rgb, axis=2)
    
    # 1. Background Subtraction
    print("Estimating background (this may take a moment)...")
    # Sigma clipping to ignore stars when estimating background
    sigma_clip = SigmaClip(sigma=3.0)
    bkg_estimator = MedianBackground()
    
    # Box size: size of the box to estimate background in. 
    # Needs to be larger than the stars but smaller than large scale variations.
    # For a high res image, 50x50 or 100x100 is reasonable.
    bkg = Background2D(gray, (50, 50), filter_size=(3, 3),
                       sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
    
    print("Subtracting background...")
    gray_bkg_sub = gray - bkg.background
    
    # 2. Denoising (Wavelet)
    print("Denoising (Wavelet) - this is computationally intensive...")
    # Wavelet denoising is effective for preserving features while removing noise
    # We pass the background subtracted image. 
    # skimage often converts to float [0, 1], so we handle that.
    gray_denoised = denoise_wavelet(gray_bkg_sub, channel_axis=None, rescale_sigma=True)
    
    # Check range of denoised image to ensure compatibility
    print(f"Denoised image range: {gray_denoised.min():.4f} to {gray_denoised.max():.4f}")
    
    # 3. Star Detection
    print("Calculating statistics on refined image...")
    mean, median, std = sigma_clipped_stats(gray_denoised, sigma=3.0)
    print(f"Refined Image - Mean: {mean:.6f}, Median: {median:.6f}, Std: {std:.6f}")
    
    print("Detecting stars...")
    # Since we subtracted background, the median should be close to 0.
    # We detect peaks above a threshold.
    threshold = 5.0 * std
    daofind = DAOStarFinder(fwhm=4.0, threshold=threshold) 
    sources = daofind(gray_denoised) # Background is already subtracted
    
    if sources is None:
        print("No stars found.")
    else:
        print(f"Found {len(sources)} stars.")
        
        # Save results
        sources.write('refined_stars_found.csv', format='csv', overwrite=True)
        
        # Plotting
        plt.figure(figsize=(20, 20))
        # Visualize with some contrast stretching
        plt.imshow(gray_denoised, cmap='gray', origin='lower', vmin=median-std, vmax=median+10*std)
        plt.scatter(sources['xcentroid'], sources['ycentroid'], s=5, edgecolor='red', facecolor='none', label='Stars')
        plt.title(f"Refined Detection: {len(sources)} Stars\n(Bg Subtracted + Wavelet Denoised)")
        plt.legend()
        plt.savefig('refined_star_detection.png')
        print("Plot saved to refined_star_detection.png")

    # Export refined image at original resolution
    print("Saving refined image...")
    
    # Robust scaling using percentiles to handle hot pixels/artifacts
    # Clip background at 1st percentile (keep it dark but not necessarily 0)
    # Clip highlights at 99.9th percentile (stars)
    vmin = np.nanpercentile(gray_denoised, 1)
    vmax = np.nanpercentile(gray_denoised, 99.9)
    
    print(f"Scaling image with vmin={vmin:.2f}, vmax={vmax:.2f}")
    
    refined_norm = (gray_denoised - vmin) / (vmax - vmin)
    refined_norm = np.clip(refined_norm, 0, 1)
    
    # Apply a slight gamma correction to bring out fainter stars
    refined_norm = np.power(refined_norm, 1.0/2.2)
    
    refined_uint8 = (refined_norm * 255).astype(np.uint8)
    
    imageio.imwrite('refined_image.png', refined_uint8)
    print("Refined image saved to refined_image.png")

if __name__ == "__main__":
    main()
