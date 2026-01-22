import pandas as pd
from database import SessionLocal, StoreVisit, init_db
from datetime import datetime
import numpy as np

def migrate():
    init_db()
    session = SessionLocal()
    
    try:
        df = pd.read_excel('DAILY REPORT (Responses).xlsx')
        # Clean numeric/NaN values
        df = df.replace({np.nan: None})
        
        # Mapping Excel columns to StoreVisit fields
        # Excel: ['Timestamp', 'STORE NAME AND CONTACT PERSON', 'PHONE NUMBER', 'TIME', 'PHOTOGRAPH', 
        #         'TOBACCO PRODUCTS INTERESTED IN/THEY DEAL IN', 'ORDER DETAILS IF CONVERTED', 
        #         'CLICK THE LINK TO RECORD LOCATION. DID YOU RECORD THE LOCATION?', 'STORE CATEGORY', 
        #         'SR NAME', 'REMARKS', 'LEAD TYPE', 'FOLLOW UP DATE', 'STORE VISIT TYPE', 'DATE', 
        #         'ADMIN REMARKS', 'LATITUDE', 'LONGITUDE']

        for _, row in df.iterrows():
            if not row['STORE NAME AND CONTACT PERSON']:
                continue
            
            # Parse Date
            visit_date = None
            if row['DATE'] and str(row['DATE']) != 'None':
                try:
                    visit_date = pd.to_datetime(row['DATE']).date()
                except:
                    pass
            if not visit_date and row['Timestamp'] and str(row['Timestamp']) != 'None':
                try:
                    visit_date = pd.to_datetime(row['Timestamp']).date()
                except:
                    pass
            if not visit_date:
                visit_date = datetime.now().date()
            
            # Parse Time
            visit_time = None
            if row['TIME'] and str(row['TIME']) != 'None':
                try:
                    # Check if it's already a time object or a string
                    if isinstance(row['TIME'], datetime):
                        visit_time = row['TIME'].time()
                    else:
                        visit_time = datetime.strptime(str(row['TIME']), "%H:%M:%S").time()
                except:
                    pass
            if not visit_time:
                visit_time = datetime.now().time()

            visit = StoreVisit(
                visit_date=visit_date,
                visit_time=visit_time,
                sr_name=str(row['SR NAME']) if row['SR NAME'] else "Unknown",
                username="sr_user",
                store_name=str(row['STORE NAME AND CONTACT PERSON']),
                visit_type=str(row['STORE VISIT TYPE']) if row['STORE VISIT TYPE'] else "NEW VISIT",
                store_category="HoReCa" if str(row['STORE CATEGORY']).upper() == "HORECA" else ("MT" if str(row['STORE CATEGORY']).upper() == "MT" else "MT"),
                phone_number=str(row['PHONE NUMBER']) if row['PHONE NUMBER'] else "",
                lead_type=str(row['LEAD TYPE']) if row['LEAD TYPE'] else "COLD",
                follow_up_date=str(row['FOLLOW UP DATE']) if row['FOLLOW UP DATE'] else None,
                products=str(row['TOBACCO PRODUCTS INTERESTED IN/THEY DEAL IN']) if row['TOBACCO PRODUCTS INTERESTED IN/THEY DEAL IN'] else "NONE",
                order_details=str(row['ORDER DETAILS IF CONVERTED']) if row['ORDER DETAILS IF CONVERTED'] else "",
                latitude=float(row['LATITUDE']) if row['LATITUDE'] else None,
                longitude=float(row['LONGITUDE']) if row['LONGITUDE'] else None,
                maps_url=f"https://www.google.com/maps?q={row['LATITUDE']},{row['LONGITUDE']}" if row['LATITUDE'] and row['LONGITUDE'] else "",
                location_recorded_answer=str(row['CLICK THE LINK TO RECORD LOCATION. DID YOU RECORD THE LOCATION?']) if row['CLICK THE LINK TO RECORD LOCATION. DID YOU RECORD THE LOCATION?'] else "NO",
                image_data="Imported from Excel" # Placeholder as we don't have base64 in excel
            )
            session.add(visit)
        
        session.commit()
        print("Migration completed successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error during migration: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    migrate()
