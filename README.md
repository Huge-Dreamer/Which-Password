# Which-Password v2.0.0

This release introduces a standalone Windows executable with a modern graphical user interface, making it easier than ever to crack password-protected archives.

## New Features
- Standalone Windows executable (no Python installation required)
- Modern graphical user interface
- Real-time progress monitoring
- Automatic archive extraction upon success
- Improved error handling and user feedback
- Memory-optimized batch processing
- Multi-threaded password cracking

## Quick Start (Windows Users)
1. Download `Which-Password.exe` from the latest release
2. Run the executable (no installation required)
3. Start using the application immediately!

## Manual Installation (For Developers)
1. Clone the repository:
   ```bash
   git clone https://github.com/Huge-Dreamer/Which-Password.git
   cd Which-Password
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python src/gui.py
   ```

## Usage

### GUI Version
1. Launch `Which-Password.exe`
2. Select your password-protected archive
3. Choose or create a password list file
4. (Optional) Configure performance settings
5. Click "Start" to begin cracking
6. Monitor progress in real-time
7. Files will automatically extract upon success

### Command Line Version
```bash
python src/which_password.py [options] archive_file password_list
```

#### Command Line Arguments
- `archive_file`: Path to the password-protected archive
- `password_list`: Path to the file containing passwords to try
- `--output-dir`: Directory to extract files (default: "extracted")
- `--max-workers`: Number of worker threads (default: 4)
- `--batch-size`: Number of passwords to process in each batch (default: 1000)
- `--memory-limit`: Memory limit in MB (default: 1024)

## Configuration
You can customize the application's behavior by creating a `config.json` file in the same directory as the executable:

```json
{
    "max_workers": 4,
    "batch_size": 1000,
    "memory_limit": 1024,
    "output_dir": "extracted"
}
```

## Performance
- Multi-threaded processing for faster password cracking
- Memory-optimized batch processing to handle large password lists
- Automatic progress saving to resume interrupted sessions
- Real-time progress monitoring and status updates

## Supported Archive Formats
- RAR (including RAR5)
- ZIP
- 7Z
- TAR
- GZ

## Notes
- The standalone executable includes all necessary dependencies
- No Python installation required
- Progress is saved automatically
- Successful passwords are logged for future reference
- 7-Zip is automatically bundled with the executable

## Disclaimer
This tool is for educational purposes only. Always ensure you have the right to access and modify the files you're working with.

## Credits
- Built with Python and PyQt6
- Uses 7-Zip for archive handling
- Developed by Huge-Dreamer

## Known Issues
None reported
