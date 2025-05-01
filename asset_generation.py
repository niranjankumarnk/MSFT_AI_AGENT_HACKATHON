import pandas as pd
from faker import Faker
import random
import os


#output directory
output_dir = 'Equipment_data'
os.makedirs(output_dir, exist_ok=True)
# Initialize Faker
fake = Faker()

# Define lists of equipment types, manufacturers, statuses, and locations
equipment_types = [
    'MRI Machine', 'Ventilator', 'ECG Monitor', 'X-Ray Machine', 'Defibrillator', 'CT Scanner',
    'PET Scanner', 'Ultrasound Machine', 'Anesthesia Machine', 'Infusion Pump', 'Patient Monitor',
    'Dialysis Machine', 'Surgical Light', 'C-Arm', 'Endoscope', 'Sterilizer', 'ECMO Machine',
    'Incubator', 'Suction Pump', 'Crash Cart', 'BP Machines', 'OT Table', 'Heart Lung Machine', 'Haemothermy'
]

manufacturers = [
    'GE Healthcare', 'Philips', 'Siemens Healthineers', 'Medtronic', 'Dräger', 'Mindray',
    'Fresenius', 'Olympus', 'Baxter', 'Stryker', 'Hitachi Medical', 'Canon Medical'
]

statuses = ['Active', 'In Repair', 'Retired']

locations = [
    'OT', 'ICU', 'CATH LAB', 'GENERAL WARD', 'CT-ICU', 'Doctors Cabin', 'ECG Room',
    'Physiotherapy Room', 'Emergency Department', 'CT', 'MRI', 'PET', 'ULTRASOUND'
]

# Generate Equipment Inventory Data
equipment_data = []
for _ in range(500):
    equipment_data.append({
        'Name/Type': random.choice(equipment_types),
        'Manufacturer': random.choice(manufacturers),
        'Model Number': fake.bothify(text='Model-###??'),
        'Serial Number': fake.bothify(text='SN-######'),
        'Location': random.choice(locations),
        'Purchase Date': fake.date_between(start_date='-10y', end_date='-1y'),
        'Warranty Expiry Date': fake.date_between(start_date='-1y', end_date='+5y'),
        'Status': random.choice(statuses)
    })

equipment_df = pd.DataFrame(equipment_data)

# -------- Maintenance Schedule Data --------
maintenance_types = ['Preventive', 'Corrective', 'Calibration']
maintenance_statuses = ['Pending', 'Completed', 'Overdue']

maintenance_data = []
for equipment in equipment_data:
    maintenance_data.append({
        'Maintenance Type': random.choice(maintenance_types),
        'Scheduled Date': fake.date_between(start_date='-1y', end_date='+1y'),
        'Completion Date': fake.date_between(start_date='-1y', end_date='today'),
        'Service Engineer Name': fake.name(),
        'Maintenance Status': random.choice(maintenance_statuses)
    })

maintenance_df = pd.DataFrame(maintenance_data)

# -------- Repair and Troubleshooting Logs --------
fault_codes = ['ERR-101', 'ERR-202', 'ERR-303', 'ERR-404', 'ERR-505']

repair_logs_data = []
for equipment in equipment_data:
    repair_logs_data.append({
        'Issue Description': fake.sentence(nb_words=6),
        'Date of Issue': fake.date_between(start_date='-1y', end_date='today'),
        'Repair Start Date': fake.date_between(start_date='-1y', end_date='today'),
        'Repair Completion Date': fake.date_between(start_date='today', end_date='+1y'),
        'Fault Codes/Error Codes': random.choice(fault_codes),
        'Repair Notes': fake.sentence(nb_words=10),
        'Parts Replaced': random.choice(['Battery', 'Sensor', 'Circuit Board', 'None']),
        'Downtime Duration': f"{random.randint(1, 15)} days",
        'Service Engineer Name': fake.name()
    })

repair_logs_df = pd.DataFrame(repair_logs_data)

# -------- Compliance and Documentation Data --------
compliance_types = ['ISO', 'FDA', 'JCI']
compliance_statuses = ['Compliant', 'Non-Compliant']

compliance_data = []
for equipment in equipment_data:
    compliance_data.append({
        'Compliance Type': random.choice(compliance_types),
        'Last Inspection Date': fake.date_between(start_date='-1y', end_date='today'),
        'Next Inspection Due Date': fake.date_between(start_date='today', end_date='+1y'),
        'Compliance Status': random.choice(compliance_statuses),
        'Documentation': fake.file_name(extension='pdf')
    })

compliance_df = pd.DataFrame(compliance_data)

# -------- User Data (Engineers and Technicians) --------
roles = ['Engineer', 'Technician', 'Admin']
certification_levels = ['OEM Certified', 'ISO Certified', 'Hospital Certified']

user_data = []
for _ in range(20):
    user_data.append({
        'Name': fake.name(),
        'Role': random.choice(roles),
        'Contact Information': fake.phone_number(),
        'Certification Levels': random.choice(certification_levels)
    })

user_df = pd.DataFrame(user_data)

# -------- Spare Parts Inventory Data --------
parts = ['Battery', 'Sensor', 'Circuit Board', 'Power Supply', 'Display Panel', 'Fan', 'Compressor']

spare_parts_data = []
for _ in range(350):
    spare_parts_data.append({
        'Equipment Type': random.choice(equipment_types),
        'Part Name': random.choice(parts),
        'Quantity Available': random.randint(1, 50),
        'Last Replenished Date': fake.date_between(start_date='-1y', end_date='today'),
        'Supplier Information': fake.company()
    })

spare_parts_df = pd.DataFrame(spare_parts_data)

# Save all data to CSV files
equipment_df.to_csv(os.path.join(output_dir ,'equipmentinventory.csv'), index=False)
maintenance_df.to_csv(os.path.join(output_dir ,'maintenanceschedule.csv'), index=False)
repair_logs_df.to_csv(os.path.join(output_dir ,'repairlogs.csv'), index=False)
compliance_df.to_csv(os.path.join(output_dir ,'compliancedata.csv'), index=False)
user_df.to_csv(os.path.join(output_dir ,'userdata.csv'), index=False)
spare_parts_df.to_csv(os.path.join(output_dir ,'sparepartsinventory.csv'), index=False)

