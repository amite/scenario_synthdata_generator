# Install dependencies
pip install -r requirements.txt

# Make script executable
chmod +x generate.py

# Flash sale scenario
python generate.py flash_sale --discount=70 --duration=4h --category=electronics

# Returns wave with custom output
python generate.py returns_wave --duration=14d --output=parquet --output-dir=./synthetic_data

# Baseline data for ML training
python generate.py baseline --customers=50000 --duration=30d --output=parquet

# Generate only specific tables
python generate.py viral_moment --tables=orders,support_tickets,cart_abandonment

# Custom scenario
python generate.py custom --config=my_scenario.json --output-dir=./custom_output

remember to use the .venv before running python