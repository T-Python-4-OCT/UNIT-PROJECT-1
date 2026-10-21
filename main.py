def display_menu():
     print("\n"+"="*40)
     print("Riyadh Smart Trip")
     print("="*40)
     print("1. Plan a Trip")
     print("2. View Saved Trips")
     print("3. View Trip Report")
     print("4. Exit")
     print("="*40)
     
     
def main():
    while True:
        display_menu()
        
        choice=input("Enter your choice (1-4):").strip()
        
        if choice=="1":
            print("\nTrip planning selected!")
            
        elif choice=="2":
            print("\nSaved trips selected!")
            
        elif choice=="3":
            print("\nTrip report selected!")
        
        elif choice=="4":
            print("\nThank you for using Riyadh Smart Trip!")
            break
            
        else:
            print("\nInvalid,Please enter a number from (1-4)")
            
            
            

if __name__=="__main__"
    main()
    
    
            