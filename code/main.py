# COMS4732: Project 1
# Maddison Hoveida
# UI: mh4572
import numpy as np
import skimage as sk
import skimage.io as skio
import skimage.transform as sktransform
import os
from skimage import exposure

def get_l2(image1, image2):
    diff = image1 - image2
    return np.sqrt(np.sum(diff ** 2))

def get_ncc(image1, image2):
    dot_product = np.sum(image1 * image2)
    norm1 = np.linalg.norm(image1)
    norm2 = np.linalg.norm(image2)
    if norm1 == 0 or norm2 == 0: return 0
    return dot_product / (norm1 * norm2)

def align_single_scale(image, anchor, window=15, metric='l2'):
    h, w = image.shape
    h_cut, w_cut = int(h * 0.1), int(w * 0.1)
    if h_cut < 1: 
        h_cut = 1
    if w_cut < 1: 
        w_cut = 1
    
    anchor_cut = anchor[h_cut:-h_cut, w_cut:-w_cut]
    
    if metric == 'l2': best_score = float('inf')
    else: best_score = float('-inf')
        
    best_shift, best_image = [0, 0], image

    for y in range(-window, window + 1):
        for x in range(-window, window + 1):
            shifted = np.roll(image, shift=(y, x), axis=(0, 1))
            shifted_cut = shifted[h_cut:-h_cut, w_cut:-w_cut]
            
            if metric == 'l2':
                score = get_l2(shifted_cut, anchor_cut)
                if score < best_score:
                    best_score, best_shift, best_image = score, [y, x], shifted
            else:
                score = get_ncc(shifted_cut, anchor_cut)
                if score > best_score:
                    best_score, best_shift, best_image = score, [y, x], shifted
                
    return best_image, best_shift

def align_pyramid(image, anchor, metric='l2', threshold=500):
    if image.shape[0] < threshold:
        return align_single_scale(image, anchor, window=15, metric=metric)

    small_image = sktransform.rescale(image, 0.5, channel_axis=None)
    small_anchor = sktransform.rescale(anchor, 0.5, channel_axis=None)
    
    _, best_shift_small = align_pyramid(small_image, small_anchor, metric=metric, threshold=threshold)
    
    next_shift = [x * 2 for x in best_shift_small]
    image_guess = np.roll(image, shift=next_shift, axis=(0, 1))
    best_image, residual_shift = align_single_scale(image_guess, anchor, window=2, metric=metric)
    
    total_shift = [next_shift[0] + residual_shift[0], next_shift[1] + residual_shift[1]]
    return best_image, total_shift


def auto_white_balance(image):
    image_white_balance = image.copy()
    
    avg_red = np.mean(image_white_balance[:, :, 0])
    avg_green = np.mean(image_white_balance[:, :, 1])
    avg_blue = np.mean(image_white_balance[:, :, 2])
    avg_gray = (avg_red + avg_green + avg_blue) / 3
    
    # if Red is too strong, scale_red will be < 1
    scale_red = avg_gray / avg_red if avg_red > 0 else 1
    scale_green = avg_gray / avg_green if avg_green > 0 else 1
    scale_blue = avg_gray / avg_blue if avg_blue > 0 else 1
    
    image_white_balance[:, :, 0] *= scale_red
    image_white_balance[:, :, 1] *= scale_green
    image_white_balance[:, :, 2] *= scale_blue
    
    return np.clip(image_white_balance, 0, 1)


def auto_contrast(image):

    p2, p98 = np.percentile(image, (2, 98))
    img_rescale = exposure.rescale_intensity(image, in_range=(p2, p98))
    
    return img_rescale

if __name__ == '__main__':
    image_names = [
        'cathedral.jpg', 'church.tif', 'emir.tif', 
        'harvesters.tif', 'icon.tif', 'italil.tif', 
        'lastochikino.tif', 'lugano.tif','melons.tif', 
        'monastery.jpg', 'self_portrait.tif', 'siren.tif',
        'three_generations.tif', 'tobolsk.jpg', 'krym.tif', 
        'peonies.tif', 'capri.tif' 
    ]
    
    # Create output directory if it doesn't exist
    if not os.path.exists('output'): 
        os.makedirs('output')

    for imname in image_names:
        try:
            print(f"Processing: {imname}")
            
            im = skio.imread(imname)
            im = sk.img_as_float(im)
            height = int(np.floor(im.shape[0] / 3.0))
            b, g, r = im[:height], im[height: 2*height], im[2*height: 3*height]

            if imname.endswith('.jpg'):
                print("  [VERIFICATION] Comparing Single-Scale vs Pyramid:")
                
                _, b_shift_single = align_single_scale(b, g, metric='l2')
                _, r_shift_single = align_single_scale(r, g, metric='l2')
                print(f"    Single-Scale -> Red: {r_shift_single} | Blue: {b_shift_single}")
                
                _, b_shift_pyr = align_pyramid(b, g, metric='l2', threshold=30)
                _, r_shift_pyr = align_pyramid(r, g, metric='l2', threshold=30)
                print(f"    Pyramid      -> Red: {r_shift_pyr} | Blue: {b_shift_pyr}")

            methods = ['l2', 'ncc']
            for method in methods:
                print(f"  Method: {method.upper()}")

                # Align
                ab, b_shift = align_pyramid(b, g, metric=method)
                ar, r_shift = align_pyramid(r, g, metric=method)
                image_out = np.dstack([ar, g, ab])

                # Crop
                bad_borders_images = ['lastochikino', 'lugano.tif']
                if any(bad_name in imname for bad_name in bad_borders_images): 
                    crop_percent = 0.08
                else: 
                    crop_percent = 0.06
                
                crop_h = int(image_out.shape[0] * crop_percent)
                crop_w = int(image_out.shape[1] * crop_percent)
                
                h_start, h_end = crop_h, -crop_h
                w_start, w_end = crop_w, -crop_w

                if 'self_portrait' in imname:
                    w_start = int(image_out.shape[1] * 0.15)

                image_out = image_out[h_start:h_end, w_start:w_end, :]

                base_name = imname.split('.')[0]

                # Save raw aligned
                raw_name = f"{base_name}_{method}.jpg"
                skio.imsave(f"output/{raw_name}", (np.clip(image_out, 0, 1) * 255).astype(np.uint8))
                print(f"      [Saved] Aligned:  output/{raw_name}")

                # White balance
                image_wb = auto_white_balance(image_out)
                wb_name = f"{base_name}_{method}_wb.jpg"
                skio.imsave(f"output/{wb_name}", (np.clip(image_wb, 0, 1) * 255).astype(np.uint8))
                print(f"      [Saved] WhiteBalance: output/{wb_name}")
                
                # Contrast
                image_final = auto_contrast(image_wb)
                final_name = f"{base_name}_{method}_final.jpg"
                skio.imsave(f"output/{final_name}", (image_final * 255).astype(np.uint8))
                print(f"      [Saved] Final:    output/{final_name}")

                # Print displacement info
                print(f"      [Displacement Info] Red: {r_shift} | Blue: {b_shift}")
                print("")

            print("-" * 60)
            
        except FileNotFoundError:
            print(f"  [ERROR] File not found: {imname}")
        except Exception as e:
            print(f"  [ERROR] Could not process {imname}: {e}")