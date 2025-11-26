#importing the needed libararies 
import struct #takes raw bytes and convert it into little endian form integers 
import os #gives you the ability to interact with the os 

# Path to the given disk image
IMAGE_PATH = r"C:\Users\HALA AHMED\Desktop\year 2\sem 1\Digital Forensics\CW Disk Image\CW Image.dd"
SECTOR_SIZE = 512 #standard sector size

#function 1 to read the mbr
def read_mbr(image_path): #reading the first  512 bytes
    with open(image_path, "rb") as f: #opens in read binary mode in 'file'
        mbr = f.read(SECTOR_SIZE)  # first 512 bytes is read here
        #mbr=f.read(512)= same code but the first version is better for usability and flow
    return mbr #returns the value 

#function 2 to detect the partitions
def detected_partitions(mbr_data):
    partitions = [] #DICTONARIES GET ADDED TO IT
    # Partition entries are 16 bytes each, starting at offset 446
    for i in range(4):
        offset = 446 + i * 16 #to reach to the correct address each time 
        entry = mbr_data[offset:offset + 16] #entry= one partition (each time, if found)

        booting_status = entry[0] # status = bootable or not , 0x80 = bootable, 0x00 = non-bootable
        partition_type = entry[4] # partition type ID
        start_sector = struct.unpack("<I", entry[8:12])[0] #4bytes of each entry= 32 bits = little endian order= start sector , returned as an integer
        total_sectors = struct.unpack("<I", entry[12:16])[0]#same steps as above but total sectors
        start_offset_bytes = start_sector * SECTOR_SIZE #working with bytes + tells me where the partition is on the disk
        size_bytes = total_sectors * SECTOR_SIZE #converts the partition sectors into bytes to convert to gb
        size_gb = size_bytes / (1024 ** 3)

        partitions.append({ #all of this is one index of the list
            "index": i + 1,
            "bootable": (booting_status == 0x80), #true if this condition is met
            "type_hex": f"0x{partition_type:02X}",
            "start_sector": start_sector,
            "total_sectors": total_sectors,
            "start_offset_bytes": start_offset_bytes,
            "size_bytes": size_bytes,
            "size_gb": size_gb
        })
    return partitions

def main(): #main function where the code is all getting connected to generate 
    if not os.path.exists(IMAGE_PATH):
        print(f"Image does not exist: {IMAGE_PATH}")
    else:
        print(f"Analyzing partition table for: {IMAGE_PATH}\n")

    mbr = read_mbr(IMAGE_PATH) #so i could take the result of the function and input it into another 
    partitions = detected_partitions(mbr)

    if partitions==False:
        print("No valid partitions found in MBR.")
        return

    for p in partitions:
        print(f"Partition {p['index']}:")
        print(f"Bootable: {p['bootable']}")
        print(f"Type (hex): {p['type_hex']}")
        print(f"Start sector: {p['start_sector']}")
        print(f"Total sectors:{p['total_sectors']}")
        print(f"Start offset:{p['start_offset_bytes']} bytes")
        print(f"Approx size:{p['size_gb']:.2f} GB")
        print() #leaves a line instead of typing /n each time in each message
#executable step 
if __name__ == "__main__": 
    main() #provokes all the functions inside the main function