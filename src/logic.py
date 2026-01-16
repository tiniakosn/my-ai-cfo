def calculate_buckets(monthly_savings):
    """
    Αυτή η συνάρτηση παίρνει το ποσό που αποταμίευσες αυτόν τον μήνα
    και το μοιράζει στους κουμπαράδες σου βάσει ποσοστών.
    """
    
    # 1. Ορίζουμε τους Στόχους (Configuration)
    # Σε μια κανονική εφαρμογή, αυτά θα ήταν σε βάση δεδομένων.
    car_goal = 5500  # Στόχος για αμάξι
    trip_goal = 700  # Στόχος για Κοπεγχάγη
    
    # 2. Υποθέτουμε ότι έχεις ήδη μαζέψει κάποια χρήματα (Simulated Data)
    # Ας πούμε ότι έχεις ήδη 1000€ στο αμάξι και 100€ για το ταξίδι.
    current_car_fund = 1000
    current_trip_fund = 100
    
    # 3. Ο Κανόνας Διαμοιρασμού (Business Logic)
    # Ας πούμε ότι από όσα περισσεύουν τον μήνα:
    # Το 80% πάει στο Αμάξι
    # Το 20% πάει στο Ταξίδι
    
    # Αν η αποταμίευση είναι αρνητική (μπήκες μέσα), δεν προσθέτουμε τίποτα (0)
    allocatable_savings = max(0, monthly_savings)
    
    added_to_car = allocatable_savings * 0.80
    added_to_trip = allocatable_savings * 0.20
    
    # 4. Υπολογισμός Νέων Υπολοίπων
    new_car_total = current_car_fund + added_to_car
    new_trip_total = current_trip_fund + added_to_trip
    
    # 5. Επιστροφή των αποτελεσμάτων (ως Dictionary)
    return {
        "car": {
            "name": "Car Fund (Goal: 5.5k)",
            "current": new_car_total,
            "goal": car_goal,
            "percent": new_car_total / car_goal,
            "added_this_month": added_to_car
        },
        "trip": {
            "name": "Copenhagen (Goal: 700€)",
            "current": new_trip_total,
            "goal": trip_goal,
            "percent": new_trip_total / trip_goal,
            "added_this_month": added_to_trip
        }
    }