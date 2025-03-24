# Which-Password

A powerful and efficient password-protected archive cracker that uses system resources optimally while maintaining stability.

## Features

- Supports multiple archive formats (RAR, ZIP, 7Z, TAR, GZ)
- Multi-threaded password cracking with optimal resource utilization
- Automatic system resource detection and optimization
- Memory-aware batch processing
- Progress tracking with detailed statistics
- Configurable timeout and retry limits
- Cross-platform support (Windows, Linux, macOS)
- High-priority process execution
- Automatic 7-Zip detection and integration

## Requirements

- Python 3.8 or higher
- 7-Zip installed on your system
- Windows: 7-Zip installed in default location or specified in config
- Linux/macOS: 7-Zip installed and available in PATH

## Installation

1. Clone the repository:
```bash
git clone https://github.com/which-password/Which-Password.git
cd Which-Password
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Configure settings in `config/config.json`:
```json
{
    "max_workers": 8,
    "timeout": 0,
    "output_dir": "extracted",
    "save_successful": true,
    "successful_passwords_file": "successful_passwords.txt",
    "supported_formats": [".rar", ".zip", ".7z", ".tar", ".gz"],
    "retry_limit": 1000,
    "log_level": "INFO",
    "sevenzip_path": "",
    "batch_size": 1000,
    "memory_limit": 8589934592,
    "cpu_priority": "high"
}
```

## Usage

Basic usage:
```bash
python src/which_password.py archive.7z --passwords passwords.txt
```

Advanced options:
```bash
python src/which_password.py archive.7z --passwords passwords.txt --config custom_config.json
```

### Command Line Arguments

- `archive`: Path to the archive file (required)
- `--passwords`: Path to password file (default: PWD.txt)
- `--config`: Path to config file (default: config/config.json)

## Configuration

The script automatically detects and optimizes for your system's capabilities:
- CPU cores and available memory
- Optimal worker count
- Memory limits
- Process priority

You can override these settings in the config file.

## Performance

- Uses 2x CPU cores (capped at 16 workers)
- Implements memory-aware batch processing
- Sets high process priority
- Provides detailed progress tracking
- Handles system resource limits gracefully

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- 7-Zip for providing the archive handling capabilities
- All contributors who have helped improve this project
