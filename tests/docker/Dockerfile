FROM python:3.11-slim

LABEL maintainer="Cribl Ansible Collections"
LABEL description="Ansible test environment for Cribl collections"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    sshpass \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /ansible

# Install Python dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Install Ansible and required collections
RUN pip install --no-cache-dir \
    ansible>=2.9 \
    ansible-core>=2.12 \
    requests>=2.28 \
    urllib3>=1.26 \
    pyyaml>=6.0

# Create ansible configuration directory
RUN mkdir -p /etc/ansible

# Copy ansible configuration
COPY tests/docker/ansible.cfg /etc/ansible/ansible.cfg

# Copy entrypoint script
COPY tests/docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variables
ENV ANSIBLE_CONFIG=/etc/ansible/ansible.cfg
ENV ANSIBLE_HOST_KEY_CHECKING=False
ENV ANSIBLE_RETRY_FILES_ENABLED=False
ENV PYTHONUNBUFFERED=1

# Use entrypoint to build modules on startup
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["tail", "-f", "/dev/null"]

