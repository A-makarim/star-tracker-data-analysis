import json
import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs import utils as wcs_utils
from astropy.visualization import simple_norm
import matplotlib.patches as patches
import constellation_data

def annotate_image(fits_file, json_file, output_file):
    print(f"Processing {fits_file}...")
    
    if not (os.path.exists(fits_file) and os.path.exists(json_file)):
        print(f"Skipping {fits_file}: Files not found.")
        return

    print(f"Loading FITS file: {fits_file}")
    try:
        hdul = fits.open(fits_file)
        data = hdul[0].data
        header = hdul[0].header
        wcs = WCS(header)
        hdul.close()
        
        # Calculate pixel scale (degrees per pixel)
        try:
            scales = wcs_utils.proj_plane_pixel_scales(wcs)
            deg_per_pixel = scales[0] # Assuming square pixels roughly
            print(f"Pixel scale: {deg_per_pixel:.6f} deg/px")
        except Exception as e:
            print(f"Could not calculate pixel scale: {e}")
            deg_per_pixel = None
            
    except Exception as e:
        print(f"Error loading FITS file: {e}")
        return

    print(f"Loading Annotations: {json_file}")
    try:
        with open(json_file, 'r') as f:
            annotations_data = json.load(f)
            annotations = annotations_data.get('annotations', [])
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return

    print("Plotting image...")
    fig, ax = plt.subplots(figsize=(20, 15))
    
    # Normalize image for display
    if data.dtype == np.uint8:
        norm_data = data
        vmin, vmax = 0, 255
    else:
        # For raw FITS data, use simple_norm
        norm = simple_norm(data, 'sqrt', percent=99.5)
        norm_data = data
        vmin, vmax = None, None
        
    # FITS data is usually (y, x) or (channel, y, x)
    if len(data.shape) == 2:
        ax.imshow(data, cmap='gray', origin='lower', vmin=vmin, vmax=vmax)
    elif len(data.shape) == 3:
        if data.shape[0] == 3:
            img_data = np.transpose(data, (1, 2, 0))
        else:
            img_data = data
        ax.imshow(img_data, origin='lower')
    
    print(f"Overlaying {len(annotations)} annotations...")
    
    for ann in annotations:
        cx = ann['pixelx']
        cy = ann['pixely']
        names = ann.get('names', [])
        name = names[0] if names else "Unknown"
        ann_type = ann.get('type', 'unknown')
        radius = ann.get('radius', 0)
        
        # Color coding
        if ann_type == 'ngc' or ann_type == 'ic':
            color = 'cyan'
            marker = 'o'
            size = radius if radius > 0 else 20
        elif ann_type == 'bright':
            color = 'yellow'
            marker = '*'
            size = 50
        else:
            color = 'red'
            marker = 'x'
            size = 20

        # Plot marker
        if radius > 5:
            circ = patches.Circle((cx, cy), radius, linewidth=1.5, edgecolor=color, facecolor='none')
            ax.add_patch(circ)
        else:
            ax.scatter(cx, cy, s=size, c=color, marker=marker, edgecolors='none')
            
        # Add label
        ax.text(cx + 10, cy + 10, name, color=color, fontsize=12, fontweight='bold',
                bbox=dict(facecolor='black', alpha=0.5, edgecolor='none', pad=2))

    # Draw Constellation Lines
    print("Drawing constellation lines...")
    for const_name, lines in constellation_data.CONSTELLATION_LINES.items():
        lines_drawn = 0
        # Get color for this constellation, default to green
        line_color = constellation_data.CONSTELLATION_COLORS.get(const_name, 'lime')
        
        for star1_pat, star2_pat in lines:
            star1 = constellation_data.find_star_in_annotations(star1_pat, annotations)
            star2 = constellation_data.find_star_in_annotations(star2_pat, annotations)
            
            if star1 and star2:
                x1, y1 = star1['pixelx'], star1['pixely']
                x2, y2 = star2['pixelx'], star2['pixely']
                
                # Draw line
                ax.plot([x1, x2], [y1, y2], color=line_color, linewidth=1.5, alpha=0.7, linestyle='-')
                lines_drawn += 1
                
                # Calculate and annotate distance
                if deg_per_pixel:
                    dist_px = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    dist_deg = dist_px * deg_per_pixel
                    
                    # Midpoint
                    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                    
                    # Check if we have 3D distances for both stars
                    d1 = constellation_data.STAR_DISTANCES_LY.get(star1_pat)
                    d2 = constellation_data.STAR_DISTANCES_LY.get(star2_pat)
                    
                    label_text = f"{dist_deg:.1f}°"
                    
                    if d1 and d2:
                        # Law of Cosines: c^2 = a^2 + b^2 - 2ab cos(C)
                        # C is the angular separation in radians
                        theta_rad = np.radians(dist_deg)
                        dist_ly = np.sqrt(d1**2 + d2**2 - 2*d1*d2*np.cos(theta_rad))
                        label_text += f"\n{dist_ly:.0f} ly"
                    
                    # Annotate distance
                    ax.text(mx, my, label_text, color='white', fontsize=9, 
                            ha='center', va='center',
                            bbox=dict(facecolor='black', alpha=0.6, edgecolor='none', pad=1))
        
        if lines_drawn > 0:
            print(f"Drawn {lines_drawn} lines for {const_name} in {line_color}")

    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved annotated image to {output_file}")

def main():
    # Process Refined Image
    annotate_image('refined_image_new.fits', 'refined_image_annotations.json', 'annotated_refined_image.png')
    
    # Process Original Image
    annotate_image('IMG_1085_new.fits', 'IMG_1085_annotations.json', 'annotated_original_image.png')


if __name__ == "__main__":
    main()
