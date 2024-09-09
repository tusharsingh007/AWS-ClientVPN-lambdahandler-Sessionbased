import json
import boto3
from datetime import datetime, timedelta

# Initialize the EC2 client
client_vpn = boto3.client('ec2', region_name='us-east-1')

def lambda_handler(event, context):
    # Define the maximum allowed duration for a session
    max_duration = timedelta(minutes=1)  # Adjust this duration as needed

    # Set the Client VPN endpoint ID
    client_vpn_endpoint_id = 'replace_with_clientVPNendpointID'

    # Check for existing connections
    response = client_vpn.describe_client_vpn_connections(
        ClientVpnEndpointId=client_vpn_endpoint_id,
        Filters=[
            {
                "Name": "status",
                "Values": ["active"]
            }
        ]
    )

    if len(response["Connections"]) > 0:
        for connection in response["Connections"]:
            connection_id = connection["ConnectionId"]
            start_time = connection["ConnectionEstablishedTime"]
            print(f"Connection {connection_id} started at: {start_time}")

            # Adjust this format string to match the timestamp format in your response
            try:
                # If the format returned is '%Y-%m-%d %H:%M:%S'
                start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                print(f"Error parsing start time: {e}")
                continue

            current_time = datetime.utcnow()

            # Calculate the duration the session has been active
            duration = current_time - start_time
            print(f"Connection {connection_id} has been active for: {duration}")

            # Terminate the connection if it has been active for more than the maximum allowed duration
            if duration > max_duration:
                print(f"Terminating connection {connection_id} due to session timeout")
                client_vpn.terminate_client_vpn_connections(
                    ClientVpnEndpointId=client_vpn_endpoint_id,
                    ConnectionId=connection_id
                )
                print(f"Closed connection {connection_id} after {duration} of activity")

    return {
        "statusCode": 200,
        "body": json.dumps("Checked and terminated old sessions as needed.")
    }
            
