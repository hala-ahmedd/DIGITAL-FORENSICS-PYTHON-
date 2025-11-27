import struct
import os

IMAGE_PATH = "disk.dd"   # <-- change your image path here

def read_mbr_partitions(mbr):
    partitions = []
    for i in range(4):
        entry_offset = 446 + i * 16
        entry = mbr[entry_offset: entry_offset + 16]

        status = entry[0]
        part_type = entry[4]
        lba_start = struct.unpack_from("<I", entry, 8)[0]
        sectors = struct.unpack_from("<I", entry, 12)[0]

        partitions.append({
            "index": i + 1,
            "status": status,
            "type": part_type,
            "lba_start": lba_start,
            "sectors": sectors
        })
    return partitions


def check_partitions(image_path):
    size = os.path.getsize(image_path)

    print(f"Image size: {size} bytes ({size/1024/1024:.2f} MB)")
    print("="*60)

    with open(image_path, "rb") as f:
        mbr = f.read(512)

    if len(mbr) < 512:
        print("ERROR: MBR too small or unreadable.")
        return

    # Boot signature check
    if mbr[510] != 0x55 or mbr[511] != 0xAA:
        print("⚠️  WARNING: MBR signature is invalid (should be 0x55AA).")

    partitions = read_mbr_partitions(mbr)

    print("\nPartition Table:")
    print("-"*60)

    for p in partitions:
        print(f"Partition {p['index']}:")
        print(f"  Type:        0x{p['type']:02X}")
        print(f"  LBA Start:   {p['lba_start']}")
        print(f"  Sectors:     {p['sectors']}")

        # Basic corruption checks
        errors = []

        if p["type"] == 0x00:
            errors.append("Unused entry")

        if p["lba_start"] == 0:
            if p["type"] != 0x00:
                errors.append("Starts at LBA 0 (likely invalid)")

        end_lba = p["lba_start"] + p["sectors"]
        if end_lba * 512 > size:
            errors.append("Partition exceeds disk size")

        if p["sectors"] == 0 and p["type"] != 0x00:
            errors.append("Zero sectors (corrupt entry)")

        if errors:
            print("  ⚠️  Issues detected:")
            for e in errors:
                print("    -", e)
        else:
            print("  ✔️ Looks OK")

        print("-"*60)


if __name__ == "__main__":
    check_partitions(IMAGE_PATH)