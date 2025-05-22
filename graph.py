
import matplotlib.pyplot as plt
import csv
import os
from matplotlib.ticker import MultipleLocator
from datetime import datetime

# --- Global Constants ---
RAW_DATA_DIR = "raw-data"
OUTPUT_DIR = "output"
HSTPOV2_FILENAME = "hstpov2.csv"
HSTPOV6_FILENAME = "hstpov6.csv"
UNEMPLOYMENT_FILENAME = "SeriesReport-20250522085516_7ebf1b.csv"

DEMOGRAPHIC_BREAK_INDICATORS = [
    "White Alone", "Black Alone", "Asian Alone",
    "American Indian", "Hispanic", "Two or More"
]

# Reagan presidency terms
REAGAN_TERM1_START = 1981
REAGAN_TERM1_END = 1984
REAGAN_TERM2_START = 1985
REAGAN_TERM2_END = 1988 # Technically 1989, but his presidency ended early into 1989, so it doesn't really count for that year

# Academic-friendly colors
COLOR_TERM1 = '#FFB347'  # Light Orange/Apricot
COLOR_TERM2 = '#ADD8E6'  # Light Blue

# --- Data Loading and Parsing ---
def load_poverty_data(csv_path, target_header_indicator, lines_to_skip_after_header,
                    year_col_idx, num_col_idx, pct_col_idx, header_search_in_cell=False):
    """
    Loads poverty data from a specified CSV file.

    Args:
        csv_path (str): Path to the CSV file.
        target_header_indicator (str): A string unique to the header row to start parsing.
        lines_to_skip_after_header (int): Number of lines to skip after the header is found.
        year_col_idx (int): Column index for the year.
        num_col_idx (int): Column index for the poverty number.
        pct_col_idx (int): Column index for the poverty percent.
        header_search_in_cell (bool): If True, search for header_indicator within any cellin a row. 
        If False, search only in the first cell.
    Returns:
        tuple: (years_data, poverty_numbers_data, poverty_percent_data)
    """
    years_data = []
    poverty_numbers_data = []
    poverty_percent_data = []

    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)

        data_header_found = False
        current_lines_to_skip = 0 # Use a different variable name to avoid modifying the input parameter

        for row in csv_reader:
            if not data_header_found:
                if header_search_in_cell: # For headers like in hstpov6.csv (part of a larger string)
                    if row and any(target_header_indicator in cell for cell in row):
                        data_header_found = True
                        current_lines_to_skip = lines_to_skip_after_header
                else: # For headers like in hstpov2.csv (first cell usually contains the indicator)
                    if row and target_header_indicator in row[0]:
                        data_header_found = True
                        current_lines_to_skip = lines_to_skip_after_header
                if not data_header_found: # Skip if header not yet found
                    continue

            if current_lines_to_skip > 0:
                current_lines_to_skip -= 1
                continue

            # Ensure row has enough columns and a year entry, consider year_col_idx
            if len(row) > max(year_col_idx, num_col_idx, pct_col_idx) and row[year_col_idx]:
                # Stop parsing if we hit a new demographic section
                if any(indicator in row[year_col_idx] for indicator in DEMOGRAPHIC_BREAK_INDICATORS):
                    break

                try:
                    year_str = row[year_col_idx].split(" ")[0]
                    if not year_str.isdigit():
                        continue
                    year = int(year_str)

                    number_str = row[num_col_idx].replace(",", "")
                    percent_str = row[pct_col_idx].replace(",", "")

                    if percent_str and percent_str.lower() != 'n' and percent_str.lower() != 'na' and percent_str.strip() != '':
                        years_data.append(year)
                        if number_str and number_str.lower() != 'n' and number_str.lower() != 'na' and number_str.strip() != '':
                            try:
                                poverty_numbers_data.append(int(number_str))
                            except ValueError:
                                poverty_numbers_data.append(0)
                        else:
                            poverty_numbers_data.append(0)

                        poverty_percent_data.append(float(percent_str))
                except ValueError as e:
                    print(f"Skipping row due to data conversion error: {row} - {e}")
                    continue
                except IndexError as e:
                    print(f"Skipping row due to missing columns: {row} - {e}")
                    continue
            elif not row or (not row[0] and data_header_found): # Handle empty rows or end of relevant data
                if years_data: # If we have already collected some data, assume end of section
                    break

    # Data is typically chronological; reverse to have earliest year first for plotting if needed
    years_data.reverse()
    poverty_numbers_data.reverse()
    poverty_percent_data.reverse()

    return years_data, poverty_numbers_data, poverty_percent_data

def load_unemployment_data(csv_path, target_header_indicator, lines_to_skip_after_header):
    """
    Loads unemployment data from a specified CSV file.

    Args:
        csv_path (str): Path to the CSV file.
        target_header_indicator (str): A string unique to the header row to start parsing.
        lines_to_skip_after_header (int): Number of lines to skip after the header is found.

    Returns:
        tuple: (dates_data, unemployment_rates_data)
    """
    dates_data = []
    unemployment_rates_data = []
    month_abbr = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)

        data_header_found = False
        current_lines_to_skip = 0

        for row in csv_reader:
            if not data_header_found:
                if row and target_header_indicator in row:
                    data_header_found = True
                    current_lines_to_skip = lines_to_skip_after_header
                if not data_header_found:
                    continue

            if current_lines_to_skip > 0:
                current_lines_to_skip -= 1
                continue

            # Assuming data rows start with the year
            if row and len(row) > 1 and row[0].strip().isdigit():
                year = int(row[0].strip())

                # Iterate through the month columns
                for month_idx in range(1, 13): # Columns 1 to 12 are months
                    if len(row) > month_idx and row[month_idx].strip():
                        month = month_abbr[list(month_abbr.keys())[month_idx-1]] # Get month number from index
                        rate_str = row[month_idx].strip()

                        # Handle potential 'NA' or empty values
                        if rate_str.lower() not in ['n', 'na', '']:
                            try:
                                # Create a date object for plotting (using day 1 for simplicity)

                                dates_data.append(datetime(year, month, 1))
                                unemployment_rates_data.append(float(rate_str))
                            except ValueError as e:
                                print(f"Skipping data point due to conversion error: Year={year}, Month={month}, Value={rate_str} - {e}")
                                continue
            elif not row or (not row[0] and data_header_found): # Handle empty rows or end of relevant data
                if dates_data: # If we have already collected some data, assume end of section
                    break
    return dates_data, unemployment_rates_data

# --- Plotting Function ---
def create_poverty_plot(years_list, data_list, title, ylabel, filename, color_term1, color_term2, term1_start, term1_end, term2_start, term2_end, annotate=True):
    """Creates and saves a poverty plot."""
    plt.figure(figsize=(14, 7))
    # If annotated, the main plot line will not have a label in the legend.
    # The ylabel is still used for the y-axis, but not for the legend entry of the line itself.
    # The main plot line will never have a label in the legend for any graph type based on new requirements.
    plt.plot(years_list, data_list, marker='o', linestyle='-', label="", color='black')
    plt.title(title)
    plt.xlabel('Year')
    plt.ylabel(ylabel) # Y-axis label always shown
    plt.grid(True)

    # Set x-axis ticks to be every 5 years
    min_year = min(years_list)
    max_year = max(years_list)
    plt.xticks(range(min_year - (min_year % 5), max_year + 5, 5), rotation=45)

    # Increase y-axis tick frequency
    ax = plt.gca()
    ax.yaxis.set_major_locator(MultipleLocator(2)) # Adjust the '2' for desired percent interval

    if annotate:
        # Add annotation for Reagan's first term
        plt.axvspan(term1_start, term1_end + 1, color=color_term1, alpha=0.6,
                    label=f'Reagan 1st Term ({term1_start}-{term1_end})')
        # Add annotation for Reagan's second term
        plt.axvspan(term2_start, term2_end + 1, color=color_term2, alpha=0.6,
                    label=f'Reagan 2nd Term ({term2_start}-{term2_end})')
        # Only show legend if there are items to show (i.e., the annotations)
        handles, labels = plt.gca().get_legend_handles_labels()
        if handles: # Only call legend if there are actual items to put in it.
            plt.legend()
    # No legend for non-annotated plots

    plt.tight_layout()

    # Ensure the output directory exists.
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save the plot to the output directory.
    save_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(save_path)
    # plt.show() # Uncomment for interactive display in a local environment
    plt.close()
    print(f"Plot saved: {save_path}")

def create_unemployment_plot(dates_list, data_list, title, ylabel, filename, color_term1, color_term2, term1_start, term1_end, term2_start, term2_end, annotate=True):
    """Creates and saves an unemployment plot with monthly data."""
    plt.figure(figsize=(14, 7))
    plt.plot(dates_list, data_list, linestyle='-', label="", color='black') # Removed marker for cleaner look with many points
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.grid(True)

    # Format x-axis to show years, potentially with month for clarity if needed (though years is usually sufficient for a long time series)
    plt.gcf().autofmt_xdate() # Auto-formats date on x-axis

    # Increase y-axis tick frequency (adjust '1' for desired interval)
    ax = plt.gca()
    ax.yaxis.set_major_locator(MultipleLocator(1))

    if annotate:
        # Add annotation for Reagan's first term
        # Adjust x-span for date objects; assuming term dates are year starts
        plt.axvspan(datetime(term1_start, 1, 1), datetime(term1_end + 1, 1, 1), color=color_term1, alpha=0.6,
                    label=f'Reagan 1st Term ({term1_start}-{term1_end})')
        # Add annotation for Reagan's second term
        plt.axvspan(datetime(term2_start, 1, 1), datetime(term2_end + 1, 1, 1), color=color_term2, alpha=0.6,
                    label=f'Reagan 2nd Term ({term2_start}-{term2_end})')

        # Only show legend if there are items to show (i.e., the annotations)
        handles, labels = plt.gca().get_legend_handles_labels()
        if handles: # Only call legend if there are actual items to put in it.
            plt.legend()

    plt.tight_layout()

    # Ensure the output directory exists.
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save the plot to the output directory.
    save_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(save_path)
    # plt.show() # Uncomment for interactive display in a local environment
    plt.close()
    print(f"Plot saved: {save_path}")


# --- Main Script Logic ---
def main():
    """Main function to load data from multiple CSVs and generate respective plots."""

    # Configurations for each CSV file and its corresponding plots
    plot_configurations = [
        {
            "csv_filename": HSTPOV2_FILENAME,
            "target_header": "All Races",
            "lines_to_skip": 3,
            "year_col": 0,
            "num_col": 2,  # "Number" under "Below poverty" for hstpov2.csv
            "pct_col": 3,  # "Percent" under "Below poverty" for hstpov2.csv
            "header_search_in_cell": False, # For hstpov2, header is usually in row[0]
            "plot_type": "poverty",
            "plot_title_base": "Percent of People Below Poverty in the US (All Races)",
            "plot_ylabel": "Percent (%)",
            "plot_filename_base": "poverty_percent_plot"
        },
        {
            "csv_filename": HSTPOV6_FILENAME,
            "target_header": "Below 1.25",
            "lines_to_skip": 0,
            "year_col": 0,
            "num_col": 4,  # "Number" for "Below 1.25" in hstpov6.csv
            "pct_col": 5,  # "Percent" for "Below 1.25" in hstpov6.csv
            "header_search_in_cell": True, # For hstpov6, header is part of a cell string
            "plot_type": "poverty",
            "plot_title_base": "Percent of People Below 1.25 of Poverty Level in the US (All Races)",
            "plot_ylabel": "Percent (%) Below 1.25 of Poverty Level",
            "plot_filename_base": "poverty_below_125_plot"
        },
        {
            "csv_filename": UNEMPLOYMENT_FILENAME,
            "target_header": "Year", # The row starting with Year,Jan,Feb...
            "lines_to_skip": 0, # Data starts right after this header row
            "plot_type": "unemployment",
            "plot_title_base": "US Unemployment Rate",
            "plot_ylabel": "Unemployment Rate (%)",
            "plot_filename_base": "unemployment_plot"
        }
    ]

    for config in plot_configurations:
        csv_full_path = os.path.join(RAW_DATA_DIR, config["csv_filename"])

        if config["plot_type"] == "poverty":
            years, _, poverty_percentages = load_poverty_data(
                csv_full_path,
                config["target_header"],
                config["lines_to_skip"],
                config["year_col"],
                config["num_col"],
                config["pct_col"],
                header_search_in_cell=config["header_search_in_cell"]
            )

            if not years:
                print(f"No data loaded from {csv_full_path}. Please check the CSV file and parsing logic.")
                continue  # Skip to the next configuration if data loading failed

            print(f"Processing plots for {csv_full_path}...")

            # Create the non-annotated plot
            create_poverty_plot(
                years_list=years,
                data_list=poverty_percentages,
                title=config["plot_title_base"],
                ylabel=config["plot_ylabel"],
                filename=f"{config['plot_filename_base']}.png",
                color_term1=COLOR_TERM1, color_term2=COLOR_TERM2,
                term1_start=REAGAN_TERM1_START, term1_end=REAGAN_TERM1_END,
                term2_start=REAGAN_TERM2_START, term2_end=REAGAN_TERM2_END,
                annotate=False
            )

            # Create the annotated plot
            create_poverty_plot(
                years_list=years,
                data_list=poverty_percentages,
                title=f"{config['plot_title_base']} - Annotated",
                ylabel=config["plot_ylabel"],
                filename=f"{config['plot_filename_base']}_annotated.png",
                color_term1=COLOR_TERM1, color_term2=COLOR_TERM2,
                term1_start=REAGAN_TERM1_START, term1_end=REAGAN_TERM1_END,
                term2_start=REAGAN_TERM2_START, term2_end=REAGAN_TERM2_END,
                annotate=True
            )

        elif config["plot_type"] == "unemployment":
            dates, unemployment_rates = load_unemployment_data(
                csv_full_path,
                config["target_header"],
                config["lines_to_skip"]
            )

            if not dates:
                print(f"No data loaded from {csv_full_path}. Please check the CSV file and parsing logic.")
                continue

            print(f"Processing plots for {csv_full_path}...")

            # Create the non-annotated plot
            create_unemployment_plot(
                dates_list=dates,
                data_list=unemployment_rates,
                title=config["plot_title_base"],
                ylabel=config["plot_ylabel"],
                filename=f"{config['plot_filename_base']}.png",
                color_term1=COLOR_TERM1, color_term2=COLOR_TERM2,
                term1_start=REAGAN_TERM1_START, term1_end=REAGAN_TERM1_END,
                term2_start=REAGAN_TERM2_START, term2_end=REAGAN_TERM2_END,
                annotate=False
            )

            # Create the annotated plot
            create_unemployment_plot(
                dates_list=dates,
                data_list=unemployment_rates,
                title=f"{config['plot_title_base']} - Annotated",
                ylabel=config["plot_ylabel"],
                filename=f"{config['plot_filename_base']}_annotated.png",
                color_term1=COLOR_TERM1, color_term2=COLOR_TERM2,
                term1_start=REAGAN_TERM1_START, term1_end=REAGAN_TERM1_END,
                term2_start=REAGAN_TERM2_START, term2_end=REAGAN_TERM2_END,
                annotate=True
            )


    print("\nAll requested plots created and saved (if data was available).")
    print("Interactive display (plt.show()) is commented out but available for local use.")

if __name__ == "__main__":
    main()
