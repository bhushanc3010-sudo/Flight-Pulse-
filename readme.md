Flight Pulse ✈️
---------------------------------------------------------------------------------------------------------------------------------
Flight Data Analytics & Delay Monitoring with Python, SQL, Supabase and Power BI
---------------------------------------------------------------------------------------------------------------------------------
Flight Pulse is a project I built to make flight information easier to explore and understand. It collects live flight snapshots from the Aviationstack API, prepares the records with Python, stores observations in Supabase, and presents the results in a five-page Power BI dashboard.

The idea is simple: instead of looking through raw flight records, wanted a workflow that turns them into useful views of flight activity, departure delays, airlines, airports, and routes.
---------------------------------------------------------------------------------------------------------------------------------

Project status: The pipeline and five-page Power BI report have
been built. The current setup uses live snapshots, and the amount of
data available depends on the Aviationstack plan and API coverage.
This is not a complete historical record of all flights.---------------------------------------------------------------------------------------------------------------------------------
📌 Problem Statement
Flight information can be available as individual records, but raw
records alone do not make it easy to answer practical questions:
- Which airlines appear in the collected data?
- Which departure airports and routes are represented?
- What can the available departure-delay values tell us?
- How much of the data has a known delay value or flight status?
- How can the latest collected observations be monitored in one place?
The challenge was to build an end-to-end workflow that collects flight
data, prepares it for analysis, stores it in a database, and makes it
easier to explore through a dashboard.
---------------------------------------------------------------------------------------------------------------------------------
💡 My Solution
I built a pipeline that connects data acquisition to reporting:
1. Collect: Request live flight information from the Aviationstack
   API.
2. Clean: Use Python and Pandas to prepare records and handle
   missing or inconsistent values.
3. Store: Load prepared observations into the
   public.flight_observations table in Supabase.
4. Analyze: Use Power BI measures and visuals to summarize flight
   observations, departure delays, airlines, airports, and routes.
5. Monitor: Explore the data through a five-page report.
The pipeline is modular, with separate acquisition, cleaning, and
database-loading stages.

---------------------------------------------------------------------------------------------------------------------------------
🔄 How It Works
                        Aviationstack API
                               |
                               v
                Flight Data Acquisition (Python)
                               |
                               v
                      Raw API Responses
                               |
                               v
            Cleaning & Preprocessing (Python / Pandas)
                               |
                               v
              Supabase: public.flight_observations
                               |
                               v
          Power BI Data Model, Measures & Visuals
                               |
                               v
                 Five-Page Flight Pulse Dashboard

---------------------------------------------------------------------------------------------------------------------------------

  Stage Purpose
  Acquisition Fetch flight observations using configured API filters.
  Raw data Keep API responses available for inspection, where configured.
  Cleaning Prepare records and handle missing or inconsistent values.                         
  Database loading Write prepared observations to Supabase using the project's loading/upsert logic.             
  Reporting Calculate KPIs and display comparisons supported by the available data.                      
                                      
---------------------------------------------------------------------------------------------------------------------------------                                 
Main data fields
The report uses fields from public.flight_observations, including:

record_key, snapshot_id, snapshot_time_utc, flight_date,
flight_number, airline, flight_status, departure_iata,
arrival_iata, scheduled_departure_utc, actual_departure_utc,
departure_delay_minutes, delay_status, data_source, and
loaded_at.

The current model includes departure-delay data. It does not contain a separate actual arrival-delay field, so the project should not be described as measuring true arrival delays.

---------------------------------------------------------------------------------------------------------------------------------
📊 Power BI Dashboard
The report has five pages, each focused on a different perspective.
1. Executive Overview
A high-level summary of the collected flight observations and delay-related KPIs.
What it helps me see: the overall shape of the collected data before exploring individual airlines, airports, or routes.
<img width="1000" height="580" alt="image" src="https://github.com/bhushanc3010-sudo/Flight-Pulse-/blob/main/Screenshot/Excecusive%20Overview.png" />

3. Airline Performance
Compares airlines represented in the collected observations using the available flight and departure-delay measures.

What it helps me see: how airlines in this dataset compare, while remembering that results depend on the coverage and completeness of the collected data.
<img width="1000" height="580" alt="image" src="(https://github.com/bhushanc3010-sudo/Flight-Pulse-/blob/main/Screenshot/Airline%20Performance.png)" />


3. Airport Intelligence
Explores observations by departure and destination airport using the airport codes in the data.

What it helps me see: which airports are represented and how the available departure-delay information varies by airport. The destination view still uses departure-delay values; it is not an arrival-delay measurement.
<img width="1000" height="580" alt="image" src="https://github.com/bhushanc3010-sudo/Flight-Pulse-/blob/main/Screenshot/Airport%20Intelligence.png" />

4. Route Analysis
Looks at the origin--destination pairs present in the collected records.

What it helps me see: which routes are represented and how their available flight and delay measures compare.
<img width="1000" height="580" alt="image" src="https://github.com/bhushanc3010-sudo/Flight-Pulse-/blob/main/Screenshot/Route%20Analysis.png" />

5. Flight Monitor
Provides a row-level view of flight observations, including flight number, airline, origin, destination, status, scheduled and actual departure times, departure delay, and snapshot time.

What it helps me see: the records behind the summary KPIs and whether important values are missing or unknown.
<img width="1000" height="580" alt="image" src="https://github.com/bhushanc3010-sudo/Flight-Pulse-/blob/main/Screenshot/Flight%20Monitor.png" />


---------------------------------------------------------------------------------------------------------------------------------
🧰 Tools & Technologies
  Technology Use in this project

   Pandas Data cleaning and preparation 
   Aviationstack API Live flight-data source
   Supabase / Postgress Storage for Prepared flight observations
   SQL Working with structured data and supporting analytics
   Power BI Data model, KPI cards, Filters , Tables and dashboard visuals
   Dax Calculation column and Mesures
    
---------------------------------------------------------------------------------------------------------------------------------
  Git & GitHub Version control and documentation
🎯 How This Project Is Useful
Flight Pulse brings several steps into one workflow. Instead of manually inspecting API responses, I can load flight observations into a database and explore them through a report.
- Flight-data exploration: review the airlines, airports, routes and statuses present in the collected observations.
- Departure-delay analysis: examine delay values when the source provides them.
- Data-quality awareness: identify missing delay values and unknown statuses instead of treating missing values as zero.
- Repeatable processing: run acquisition, cleaning, and loading as a pipeline.
- Analytics practice: demonstrate how API data can move through Python, a relational database, and Power BI.
---------------------------------------------------------------------------------------------------------------------------------
🌍 Project Impact

The practical value of this project is the workflow it demonstrates: raw API data becomes structured, queryable data and then a report that is easier to inspect.

For my data analytics and data engineering portfolio, it demonstrates experience with API ingestion, Python data preparation, database loading, Power BI measures, dashboard design, and data-quality considerations.

This is a portfolio project and analytical prototype. I have not measured business cost savings or operational improvements, so I do not claim quantified business results.
🧪 Data Quality & Limitations
- Live snapshots, not a complete history: historical collection is disabled in the current configuration because of API-plan limitations.
- API coverage and request limits: results depend on the Aviationstack plan, endpoint coverage, filters, and request limits.
- Missing delay values: some records may not have a usable departure-delay value. Missing values should remain missing, not be interpreted as zero delay.
- Unknown statuses: the source may not provide a clear status for every observation.
- Departure delay only: there is no separate arrival-delay field in the current data model. Airport views grouped by destination still use the available departure-delay measure.
- Snapshots and upserts: repeated runs may update existing records or add observations depending on the database keys and loading logic. A successful run does not guarantee that the table's row count increases every time.
- Power BI refresh: updating Supabase does not automatically refresh an imported copy of the data in Power BI Desktop. Refresh the model after a successful load.

These limitations matter because dashboard metrics depend on the coverage, freshness, and completeness of the underlying data.
🚀 Running the Project
These steps assume the repository includes run_pipeline.py and the src package. Confirm that the commands and environment-variable names match the code in your repository before publishing.
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
2. Create and activate a virtual environment python -m venv .venv On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
3. Install dependencies If your repository contains requirements.txt:
pip install -r requirements.txt
4. Configure environment variables Create a local .env file with the variable names expected by your code. For example, your configuration may look like this; replace the names if your code uses different ones.
AVIATIONSTACK_API_KEY=your_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_key
Never commit .env, API keys, database passwords, or service-role keys
to GitHub. Add .env to .gitignore and publish a sanitized
.env.example instead.
5. Run the full pipeline python run_pipeline.py The expected workflow is acquisition, cleaning, and loading into Supabase. Check the terminal output for errors, then verify that the expected observations are in public.flight_observations.

To run acquisition separately, if this module exists in your checkout:
python -m src.acquisition.run_acquisition
6. Refresh Power BI Open the .pbix report and select Home → Refresh. Confirm that the report reflects the latest records in Supabase. A published report may also need a configured semantic-model refresh in Power BI Service.

---------------------------------------------------------------------------------------------------------------------------------
🔐 Security
- Keep API keys and database credentials out of source control.
- Use .gitignore for .env, virtual environments, and local data files as appropriate.
- Use only the database permissions required by the pipeline.
- Check screenshots for credentials or private project details before publishing.
---------------------------------------------------------------------------------------------------------------------------------
🛣️ Possible Future Improvements
These are ideas for future work, not features I am claiming as
completed:
- Expand airport filters---for example, Delhi (DEL) and Bengaluru (BLR)---while monitoring API request limits.
- Store longer-term snapshots to support more useful time-based analysis, subject to source availability and plan limits.
- Add scheduled pipeline execution and failure notifications.
- Automate Power BI refresh after a successful database load.
- Add more data-quality checks and pipeline run logging.
- Add arrival-delay analysis if a reliable arrival-delay field becomes available.

---------------------------------------------------------------------------------------------------------------------------------
📁 Suggested Repository Structure
Adjust this example to match the files actually present in your repository.
FlightPulse/
├── src/
│   ├── acquisition/
│   │   ├── flight_api.py
│   │   └── run_acquisition.py
│   ├── cleaning/
│   └── database/
│       └── load_flights.py
├── data/
│   ├── raw/              # Usually keep local API responses out of Git
│   └── processed/        # Usually keep generated data out of Git
├── screenshots/
│   ├── 01-executive-overview.png
│   ├── 02-airline-performance.png
│   ├── 03-airport-intelligence.png
│   ├── 04-route-analysis.png
│   └── 05-flight-monitor.png
├── run_pipeline.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

---------------------------------------------------------------------------------------------------------------------------------
🙋 What I Learned
Building Flight Pulse helped me connect the steps involved in turning external API data into a usable analytics report. I worked with Python data processing, database loading, structured data in Supabase, and Power BI reporting in one workflow. It also reinforced an important lesson: missing data, limited API coverage, and refresh behavior need to be handled explicitly if dashboard metrics are going to be interpreted correctly.
