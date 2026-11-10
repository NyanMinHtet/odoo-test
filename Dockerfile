# Odoo Docker image based on Odoo 17.0
FROM odoo:17.0

# Run as root during build, switch to odoo user at runtime
USER root

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy custom addons
COPY addons/ /mnt/extra-addons/

# Set ownership for odoo user
RUN chown -R odoo:odoo /mnt/extra-addons

# Switch to odoo user for runtime
USER odoo

# Default command (handled by docker-compose)
CMD ["odoo"]
