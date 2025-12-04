import pprint
from py3dbp import Packer, Bin, Item
from collections import defaultdict
from io import StringIO
import sys
from fastapi import FastAPI
from pydantic import BaseModel

class BoxInput(BaseModel):
    name: str
    length: float
    width: float
    height: float
    quantity: int


class PackingRequest(BaseModel):
    pallet_l: float
    pallet_w: float
    pallet_h: float
    boxes: list[BoxInput]

def pack_boxes(pallet_l, pallet_w, pallet_h, boxes):
    """Multi-pallet packing that returns all text instead of printing."""
    
    output = StringIO()
    def write(*args):
        output.write(" ".join(map(str, args)) + "\n")
    
    # Create all items
    all_items = []
    for box_id, l, w, h, qty in boxes:
        for i in range(qty):
            all_items.append(Item(f"{box_id}-{i+1}", l, w, h, 1))
    
    write(f"Total items to pack: {len(all_items)}")
    write("Box breakdown:")
    for box_id, l, w, h, qty in boxes:
        write(f"  {box_id}: {qty} boxes ({l}x{w}x{h})")
    
    pallets = []
    remaining_items = all_items.copy()
    pallet_num = 1
    max_pallets = 10
    
    while remaining_items and pallet_num <= max_pallets:
        write(f"\n=== Packing Pallet {pallet_num} ===")
        write(f"Remaining items: {len(remaining_items)}")
        
        packer = Packer()
        packer.add_bin(Bin(f"Pallet-{pallet_num}", pallet_l, pallet_w, pallet_h, 1000))
        
        for item in remaining_items:
            packer.add_item(item)
        
        packer.pack()
        
        bin_result = packer.bins[0]
        fitted_items = bin_result.items
        unfitted_items = bin_result.unfitted_items
        
        write(f"Fitted in pallet {pallet_num}: {len(fitted_items)} items")
        write(f"Unfitted after pallet {pallet_num}: {len(unfitted_items)} items")
        
        box_counts = defaultdict(int)
        for item in fitted_items:
            box_type = item.name.split('-')[0]
            box_counts[box_type] += 1
        
        write(f"Box counts in pallet {pallet_num}: {dict(box_counts)}")
        
        pallets.append({
            'name': f"Pallet-{pallet_num}",
            'fitted': fitted_items,
            'unfitted': unfitted_items,
            'box_counts': dict(box_counts)
        })
        
        remaining_items = unfitted_items.copy()
        
        if len(fitted_items) == 0:
            write("No items fitted in this pallet - stopping")
            break
            
        pallet_num += 1
    
    return pallets, remaining_items, output.getvalue()


def generate_report(pallets, unfitted, pallet_l, pallet_w, pallet_h):
    """Return detailed text report instead of printing."""
    
    output = StringIO()
    def write(*args):
        output.write(" ".join(map(str, args)) + "\n")
    
    write("\n" + "="*20 + " FINAL PALLET REPORT " + "="*20)
    
    total_fitted = 0
    total_volume_used = 0
    pallet_volume = pallet_l * pallet_w * pallet_h
    
    for pallet in pallets:
        write(f"\n🔹 {pallet['name']}")
        write(f"Dimensions: {pallet_l}x{pallet_w}x{pallet_h}")
        write(f"Max Volume: {pallet_volume}")
        
        write("\n📦 Box counts:")
        for box_type, count in pallet['box_counts'].items():
            write(f"   • {box_type}: {count}")
        
        volume_used = sum(item.get_volume() for item in pallet['fitted'])
        total_volume_used += volume_used
        occupancy = (volume_used / pallet_volume) * 100
        total_fitted += len(pallet['fitted'])
        
        write(f"\n📐 Volume occupied: {volume_used:.3f}")
        write(f"🎯 Occupancy: {occupancy:.2f}%")
        
        write("\n✔ FITTED ITEMS:")
        for item in pallet['fitted']:
            write(f"    {item.string()}")
        
        write("\n❌ UNFITTED ITEMS:")
        for item in pallet['unfitted']:
            write(f"    {item.string()}")
        
        write("\n" + "-" * 50)
    
    write(f"\n{'='*20} SUMMARY {'='*20}")
    write(f"Total Pallets Used: {len(pallets)}")
    write(f"Total Items Packed: {total_fitted}")
    write(f"Total Items Unpacked: {len(unfitted)}")
    utilization = (total_volume_used / (len(pallets) * pallet_volume)) * 100 if pallets else 0
    write(f"Overall Volume Utilization: {utilization:.1f}%")
    
    if unfitted:
        write(f"\n⚠️  WARNING: {len(unfitted)} items could not be packed!")
    else:
        write(f"\n✅ SUCCESS: All items packed successfully!")
    
    return output.getvalue()

app=FastAPI()
# ===============================
# 🌐 API WRAPPER FUNCTION
# ===============================
@app.post("/calculate")
def run_packing_api(data: PackingRequest):
    """Main API function that returns EVERYTHING as JSON"""
    boxes=[
        [b.name, b.length, b.width, b.height, b.quantity]
        for b in data.boxes ]
    pallets, unfitted, prep_text = pack_boxes(data.pallet_l,data.pallet_w,data.pallet_h,boxes)
    report_text = generate_report(pallets, unfitted, data.pallet_l,data.pallet_w,data.pallet_h)
    
    return {
        #"prep_output": prep_text,
        #"report_output": report_text,
        "total_pallets": len(pallets),
        #"unfitted_count": len(unfitted),
        "pallets": [
            {
                "name": p["name"],
                "box_counts": p["box_counts"],
                #"fitted": [item.name for item in p["fitted"]],
                #"unfitted": [item.name for item in p["unfitted"]],
            }
            for p in pallets
        ],
        #"unfitted_items": [item.name for item in unfitted],
    }
print(run_packing_api(PackingRequest(**{
  "pallet_l": 10,
  "pallet_w": 10,
  "pallet_h": 10,
  "boxes": [
    {"name": "C", "length": 5, "width": 5, "height": 5, "quantity": 4},
    {"name": "A", "length": 10, "width": 10, "height": 10, "quantity": 5},
    {"name": "B", "length": 4, "width": 3, "height": 2, "quantity": 18}
  ]
})))
