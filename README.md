# Which-Password

"Which-Password" is a simple batch script that attempts to extract password-protected RAR, ZIP, and 7z files using a list of passwords stored in a text file. The script utilizes the command-line version of 7-Zip for extraction.

## Features

- Supports RAR, ZIP, and 7z file formats.
- Reads passwords from a specified text file.
- Provides feedback on the password attempts and the result of the extraction.
- Keeps the Command Prompt open to display results.

## Requirements

- Windows operating system.
- [7-Zip](https://www.7-zip.org/) installed (make sure to have `7z.exe` available in your system or specify the path in the script).
- A text file containing the list of passwords (named `PWD.txt`).

## Installation

1. **Download 7-Zip**: If you haven't already, download and install 7-Zip from [7-Zip's official website](https://www.7-zip.org/).

2. **Add 7-Zip to the PATH Environment Variable** (optional but recommended):
   - Locate the installation directory of 7-Zip, typically `C:\Program Files\7-Zip\`.
   - Right-click on "This PC" or "Computer" and select "Properties".
   - Click on "Advanced system settings" on the left.
   - In the System Properties window, click on the "Environment Variables" button.
   - In the Environment Variables window, find the "Path" variable in the "System variables" section and select it, then click "Edit".
   - Click "New" and add the path to the 7-Zip installation directory (e.g., `C:\Program Files\7-Zip\`).
   - Click "OK" to close all dialog boxes.

3. **Clone or Download the Repository**: Clone this repository or download it as a ZIP file.

4. **Place Your Files**: Ensure that the following files are in the same directory as the batch script:
   - The archive file you want to extract (e.g., `example.rar`, `example.zip`, or `example.7z`).
   - A text file named `PWD.txt` containing the list of passwords (one password per line).

## Usage

1. Open Command Prompt.
2. Navigate to the directory where the batch script is located.
3. Run the script by typing:
   ```cmd
   extract_archive.bat

## Disclaimer

This tool is designed and provided solely for educational purposes. Any misuse of this tool for malicious or illegal activities is strictly forbidden. The author accepts no responsibility for any improper use of this tool.

## Credits

This tool was developed by Huge Dreamer for educational purposes.
