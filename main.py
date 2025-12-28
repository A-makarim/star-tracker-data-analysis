import rawpy
import numpy as np
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

def main():
    image_path = 'IMG_1085.CR2'
    
    print(f"Loading image: {image_path}")
    try:
        with rawpy.imread(image_path) as raw:
            rgb = raw.postprocess()
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Convert to grayscale
    # Simple average or luminosity method
    gray = np.mean(rgb, axis=2)
    
    print("Calculating statistics...")
    mean, median, std = sigma_clipped_stats(gray, sigma=3.0)
    print(f"Mean: {mean:.2f}, Median: {median:.2f}, Std: {std:.2f}")

    print("Detecting stars with varying FWHM...")
    
    results = []
    
    # Iterate FWHM from 1 to 10
    for fwhm in range(4, 5):
        print(f"Processing FWHM = {fwhm}...")
        daofind = DAOStarFinder(fwhm=float(fwhm), threshold=3.*std)
        sources = daofind(gray - median)
        
        count = len(sources) if sources is not None else 0
        results.append((fwhm, sources))
        
        # Plot individual detection
        plt.figure(figsize=(20, 20))
        plt.imshow(gray, cmap='gray', origin='lower', vmin=mean-std, vmax=mean+5*std)
        if sources is not None:
            plt.scatter(sources['xcentroid'], sources['ycentroid'], s=5, edgecolor='red', facecolor='none', label='Stars')
        plt.title(f"FWHM: {fwhm}, Detected {count} Stars")
        plt.legend()
        plt.savefig(f'star_detection_fwhm_{fwhm}.png')
        plt.close()
        print(f"Saved star_detection_fwhm_{fwhm}.png")

        if sources is not None:
            # Plotting statistics
            plt.figure(figsize=(15, 10))

            # Magnitude Histogram
            plt.subplot(2, 2, 1)
            plt.hist(sources['mag'], bins=30, color='skyblue', edgecolor='black')
            plt.title(f'Star Magnitude Distribution (FWHM={fwhm})')
            plt.xlabel('Magnitude')
            plt.ylabel('Count')

            # Flux Histogram
            plt.subplot(2, 2, 2)
            plt.hist(sources['flux'], bins=30, color='lightgreen', edgecolor='black')
            plt.title(f'Star Flux Distribution (FWHM={fwhm})')
            plt.xlabel('Flux')
            plt.ylabel('Count')
            
            # Peak vs Flux
            plt.subplot(2, 2, 3)
            plt.scatter(sources['flux'], sources['peak'], alpha=0.5, s=10)
            plt.title(f'Peak Value vs Flux (FWHM={fwhm})')
            plt.xlabel('Flux')
            plt.ylabel('Peak Value')

            # Roundness vs Sharpness (if available)
            if 'sharpness' in sources.colnames and 'roundness1' in sources.colnames:
                plt.subplot(2, 2, 4)
                plt.scatter(sources['sharpness'], sources['roundness1'], alpha=0.5, s=10)
                plt.title(f'Sharpness vs Roundness (FWHM={fwhm})')
                plt.xlabel('Sharpness')
                plt.ylabel('Roundness')

            plt.tight_layout()
            plt.savefig(f'star_statistics_fwhm_{fwhm}.png')
            plt.close()
            print(f"Saved star_statistics_fwhm_{fwhm}.png")

            # DBSCAN Clustering
            coords = np.transpose((sources['xcentroid'], sources['ycentroid']))
            # eps=100 pixels, min_samples=5 stars to form a cluster
            db = DBSCAN(eps=35, min_samples=12).fit(coords)
            labels = db.labels_
            n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
            
            plt.figure(figsize=(20, 20))
            plt.imshow(gray, cmap='gray', origin='lower', vmin=mean-std, vmax=mean+5*std)
            
            # Plot noise
            noise_mask = labels == -1
            plt.scatter(coords[noise_mask, 0], coords[noise_mask, 1], s=5, c='gray', alpha=0.5, label='Noise')
            
            # Plot clusters
            unique_labels = set(labels)
            colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
            for k, col in zip(unique_labels, colors):
                if k == -1:
                    continue
                class_member_mask = (labels == k)
                plt.scatter(coords[class_member_mask, 0], coords[class_member_mask, 1], s=20, color=col, label=f'Cluster {k}')
            
            plt.title(f"FWHM: {fwhm}, Clusters: {n_clusters_}")
            plt.savefig(f'star_clusters_fwhm_{fwhm}.png')
            plt.close()
            print(f"Saved star_clusters_fwhm_{fwhm}.png")

    # Combined plot of detections
    print("Creating combined plot...")
    fig, axes = plt.subplots(2, 5, figsize=(25, 10))
    axes = axes.flatten()
    
    for idx, (fwhm, sources) in enumerate(results):
        ax = axes[idx]
        ax.imshow(gray, cmap='gray', origin='lower', vmin=mean-std, vmax=mean+5*std)
        if sources is not None:
            ax.scatter(sources['xcentroid'], sources['ycentroid'], s=1, edgecolor='red', facecolor='none')
        ax.set_title(f"FWHM: {fwhm}, Stars: {len(sources) if sources is not None else 0}")
        ax.axis('off')
        
    plt.tight_layout()
    plt.savefig('star_detection_all_fwhm.png')
    print("Saved star_detection_all_fwhm.png")

if __name__ == "__main__":
    main()
