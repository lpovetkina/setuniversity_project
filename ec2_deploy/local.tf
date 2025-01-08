locals {
  vpc_cidr = "10.0.0.0/16"
  azs      = slice(data.aws_availability_zones.available.names, 0, 3)

  user_data = <<-EOF
#!/bin/bash
# Update and install dependencies
sudo apt update -y
sudo apt install -y software-properties-common build-essential wget git gcc g++ make libpoppler-dev

# Remove any existing sqlite3 and install necessary dependencies
sudo apt-get remove -y sqlite3
sudo apt-get install -y build-essential tcl wget

# Download and install SQLite 3.35.0 or higher
wget https://www.sqlite.org/2024/sqlite-autoconf-3470200.tar.gz
tar xvfz sqlite-autoconf-3470200.tar.gz
cd sqlite-autoconf-3470200
./configure
make
sudo make install

# Check version to ensure it's >= 3.35.0
sqlite3 --version

# Return to parent directory
cd ..

# Add Python 3.11 repository and install
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update -y
sudo apt install -y python3.11 python3.11-venv python3.11-dev poppler-utils

# Set up Python 3.11 virtual environment
mkdir -p /home/ubuntu/streamlit-env
python3.11 -m venv /home/ubuntu/streamlit-env/venv
source /home/ubuntu/streamlit-env/venv/bin/activate

# Upgrade pip and install Python libraries
pip install --upgrade pip
pip install streamlit pdf2image easyocr

mkdir -p /home/ubuntu/streamlit-app

# Clone your Streamlit app repository (replace with your repo URL)


# Set ownership for the ubuntu
sudo chown -R ubuntu:ubuntu /home/ubuntu/streamlit-app
sudo chmod u+w /home/ubuntu/streamlit-app
ls 
# Navigate to the app directory
cd /home/ubuntu/streamlit-app

# Install dependencies from requirements.txt inside venv
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

# Create a systemd service for the Streamlit app
sudo bash -c 'cat << EOF > /etc/systemd/system/streamlit-app.service
[Unit]
Description=Streamlit Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/streamlit-app
ExecStart=/bin/bash -c "source /home/ubuntu/streamlit-env/venv/bin/activate && /home/ubuntu/streamlit-env/venv/bin/python -m streamlit run /home/ubuntu/streamlit-app/src/main.py --server.port 8501 --server.address 0.0.0.0"
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
EOF'

# Reload systemd to apply changes and start the service
sudo systemctl daemon-reload
sudo systemctl enable streamlit-app.service
sudo systemctl start streamlit-app.service

# Log application setup completion
echo "Streamlit app setup complete and running!" > /home/ubuntu/streamlit-app/setup.log
EOF
}