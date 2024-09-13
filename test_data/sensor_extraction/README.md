# Sensor Extraction

This directory contains code for extracting data from sensors and exposing it through an API.

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt` 

## Usage

1. Configure sensors in `config.py`
2. Run `python app.py`
3. Access API at `http://localhost:5000/api/readings`

## Files

### app.py

The main application script. Handles interfacing with sensor hardware, processing data, and running the API server.

### stack.py 

Defines data structures and algorithms for managing the sensor data stack.

### graph_diagram.png

Diagram showing the data flow from sensors through the application components.

## Contributing

Contributions are welcome! Please follow the guidelines in `CONTRIBUTING.md`.

## License

This project is licensed under the [MIT License](LICENSE).