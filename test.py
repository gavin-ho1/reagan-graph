
import matplotlib.pyplot as plt
import csv
import os

# --- Constants ---
CSV_FILE_PATH = "hstpov2.csv"
TARGET_HEADER_INDICATOR = "All Races"
LINES_TO_SKIP_AFTER_HEADER = 3
DEMOGRAPHIC_BREAK_INDICATORS = [
    "White Alone", "Black Alone", "Asian Alone",
    "American Indian", "Hispanic", "Two or More"
]

# Reagan presidency terms
REAGAN_TERM1_START = 1981
REAGAN_TERM1_END = 1984
REAGAN_TERM2_START = 1985
REAGAN_TERM2_END = 1988

# Academic-friendly colors
COLOR_TERM1 = '#FFB347'  # Light Orange/Apricot
COLOR_TERM2 = '#ADD8E6'  # Light Blue

# --- Data Loading and Parsing ---
def load_poverty_data(csv_path):
    """Loads poverty data from the specified CSV file."""
    years_data = []
    poverty_numbers_data = []
    poverty_percent_data = []

    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        data_header_found = False
        lines_to_skip = 0
        
        for row in csv_reader:
            if not data_header_found:
                if row and TARGET_HEADER_INDICATOR in row[0]: 
                    data_header_found = True
                    lines_to_skip = LINES_TO_SKIP_AFTER_HEADER
                continue
            
            if lines_to_skip > 0:
                lines_to_skip -= 1
                continue

            if len(row) > 3 and row[0]: # Ensure row has enough columns and a year entry
                # Stop parsing if we hit a new demographic section
                if any(indicator in row[0] for indicator in DEMOGRAPHIC_BREAK_INDICATORS):
                    break 
                
                try:
                    year_str = row[0].split(" ")[0] # Expects year to be the first part of the first column
                    if not year_str.isdigit(): # Skip if year is not a number
                        continue
                    year = int(year_str)
                    
                    # Clean and convert poverty number and percent
                    number_str = row[2].replace(",", "")
                    percent_str = row[3].replace(",", "")
                    
                    # Ensure data is present and not 'N/A'
                    if number_str and percent_str and number_str.lower() != 'n' and percent_str.lower() != 'n':
                        years_data.append(year)
                        poverty_numbers_data.append(int(number_str))
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

# --- Plotting Function ---
def create_poverty_plot(years_list, data_list, title, ylabel, filename, color_term1, color_term2, term1_start, term1_end, term2_start, term2_end):
    """Creates and saves a poverty plot."""
    plt.figure(figsize=(14, 7))
    plt.plot(years_list, data_list, marker='o', linestyle='-', label=ylabel, color='black')
    plt.title(title)
    plt.xlabel('Year')
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.xticks(rotation=45)
    
    # Add annotation for Reagan's first term
    plt.axvspan(term1_start, term1_end + 1, color=color_term1, alpha=0.6, 
                label=f'Reagan 1st Term ({term1_start}-{term1_end})')
    # Add annotation for Reagan's second term
    plt.axvspan(term2_start, term2_end + 1, color=color_term2, alpha=0.6, 
                label=f'Reagan 2nd Term ({term2_start}-{term2_end})')
    
    plt.legend()
    plt.tight_layout()
    
    # Save the plot to the current working directory
    save_path = os.path.join(os.getcwd(), filename)
    plt.savefig(save_path)
    # plt.show() # Uncomment for interactive display in a local environment
    plt.close()
    print(f"Plot saved: {save_path}")

# --- Main Script Logic ---
if __name__ == "__main__":
    years, poverty_numbers, poverty_percent = load_poverty_data(CSV_FILE_PATH)

    if not years:
        print("No data loaded. Please check the CSV file and parsing logic.")
    else:
        # Create the first plot: Number of people below poverty
        create_poverty_plot(
            years, poverty_numbers,
            'Number of People Below Poverty in the US (All Races)',
            'Number of People (in thousands)',
            "poverty_number_plot.png",
            COLOR_TERM1, COLOR_TERM2,
            REAGAN_TERM1_START, REAGAN_TERM1_END,
            REAGAN_TERM2_START, REAGAN_TERM2_END
        )

        # Create the second plot: Percent of people below poverty
        create_poverty_plot(
            years, poverty_percent,
            'Percent of People Below Poverty in the US (All Races)',
            'Percent (%)',
            "poverty_percent_plot.png",
            COLOR_TERM1, COLOR_TERM2,
            REAGAN_TERM1_START, REAGAN_TERM1_END,
            REAGAN_TERM2_START, REAGAN_TERM2_END
        )

        print("Plots created and saved. Interactive display (plt.show()) is commented out but available for local use.")

