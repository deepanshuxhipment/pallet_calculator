from py3dbp import Packer, Bin, Item
from collections import defaultdict
PALLET_L, PALLET_W, PALLET_H = 10, 10, 10
boxes = [
        ["C", 5, 5, 5, 4],
        ["A", 10, 10, 10, 5], 
        ["B", 4, 3, 2, 18]
    ]
def pack_boxes_correctly(PALLET_L, PALLET_W, PALLET_H,boxes):
    """Proper multi-pallet packing with correct item distribution"""
    
    # Pallet size
    #PALLET_L, PALLET_W, PALLET_H = 10, 10, 10
    
    # Box data
    
    
    # Create all items
    all_items = []
    for box_id, l, w, h, qty in boxes:
        for i in range(qty):
            all_items.append(Item(f"{box_id}-{i+1}", l, w, h, 1))
    
    print(f"Total items to pack: {len(all_items)}")
    print("Box breakdown:")
    for box_id, l, w, h, qty in boxes:
        print(f"  {box_id}: {qty} boxes ({l}x{w}x{h})")
    
    pallets = []
    remaining_items = all_items.copy()
    pallet_num = 1
    max_pallets = 10
    
    while remaining_items and pallet_num <= max_pallets:
        print(f"\n=== Packing Pallet {pallet_num} ===")
        print(f"Remaining items: {len(remaining_items)}")
        
        # Create fresh packer for this pallet
        packer = Packer()
        packer.add_bin(Bin(f"Pallet-{pallet_num}", PALLET_L, PALLET_W, PALLET_H, 1000))
        
        # Add only remaining items
        for item in remaining_items:
            packer.add_item(item)
        
        # Pack this pallet
        packer.pack()
        
        bin_result = packer.bins[0]
        fitted_items = bin_result.items
        unfitted_items = bin_result.unfitted_items
        
        print(f"Fitted in pallet {pallet_num}: {len(fitted_items)} items")
        print(f"Unfitted after pallet {pallet_num}: {len(unfitted_items)} items")
        
        # Count box types in this pallet
        box_counts = defaultdict(int)
        for item in fitted_items:
            box_type = item.name.split('-')[0]
            box_counts[box_type] += 1
        
        print(f"Box counts in pallet {pallet_num}: {dict(box_counts)}")
        
        # Store results
        pallets.append({
            'name': f"Pallet-{pallet_num}",
            'bin': bin_result,
            'fitted': fitted_items,
            'unfitted': unfitted_items,
            'box_counts': box_counts
        })
        
        # CRITICAL: Update remaining items to only those that didn't fit
        remaining_items = unfitted_items.copy()
        
        # If no items were fitted in this pallet, stop (can't pack anything)
        if len(fitted_items) == 0:
            print("No items fitted in this pallet - stopping")
            break
            
        pallet_num += 1
    
    return pallets, remaining_items

def generate_detailed_report(pallets, unfitted):
    """Generate a comprehensive packing report"""
    
    print("\n" + "="*20 + " FINAL PALLET REPORT " + "="*20)
    
    total_fitted = 0
    total_volume_used = 0
    pallet_volume = PALLET_L* PALLET_W *PALLET_H
    
    for i, pallet in enumerate(pallets):
        print(f"\n🔹 {pallet['name']}")
        print(f"Dimensions: 48x40x66")
        print(f"Max Volume: {pallet_volume}")
        
        # Box counts
        print(f"\n📦 Box counts:")
        for box_type, count in pallet['box_counts'].items():
            print(f"   • {box_type}: {count}")
        
        # Volume calculation
        volume_used = sum(item.get_volume() for item in pallet['fitted'])
        total_volume_used += volume_used
        occupancy = (volume_used / pallet_volume) * 100
        total_fitted += len(pallet['fitted'])
        
        print(f"\n📐 Volume occupied: {volume_used:.3f}")
        print(f"🎯 Occupancy: {occupancy:.2f}%")
        
        print(f"\n✔ FITTED ITEMS:")
        for item in pallet['fitted']:
            print(f"    {item.string()}")
        
        print(f"\n❌ UNFITTED ITEMS:")
        for item in pallet['unfitted']:
            print(f"    {item.string()}")
        
        print("\n" + "-" * 50)
    
    # Summary
    print(f"\n{'='*20} SUMMARY {'='*20}")
    print(f"Total Pallets Used: {len(pallets)}")
    print(f"Total Items Packed: {total_fitted}")
    print(f"Total Items Unpacked: {len(unfitted)}")
    print(f"Overall Volume Utilization: {(total_volume_used/(len(pallets)*pallet_volume))*100:.1f}%")
    
    if unfitted:
        print(f"\n⚠️  WARNING: {len(unfitted)} items could not be packed!")
    else:
        print(f"\n✅ SUCCESS: All items packed successfully!")
 
# Run the corrected packing
pallets, unfitted = pack_boxes_correctly(PALLET_L, PALLET_W, PALLET_H,boxes)
generate_detailed_report(pallets, unfitted)