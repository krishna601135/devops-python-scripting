import boto3
from datetime import datetime, timedelta

def get_min_cpu_utilization(instance_id, region, start_time, end_time):
    # Create CloudWatch client for the specified region
    cloudwatch = boto3.client('cloudwatch', region_name=region)

    # Define metric query parameters
    metric_query = {
        'Id': 'm1',
        'MetricStat': {
            'Metric': {
                'Namespace': 'AWS/EC2',
                'MetricName': 'CPUUtilization',
                'Dimensions': [
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    },
                ]
            },
            'Period': 300,  # 5-minute intervals
            'Stat': 'Minimum',  # Minimum CPU utilization
        },
        'ReturnData': True,
    }

    # Get metric data
    response = cloudwatch.get_metric_data(
        MetricDataQueries=[metric_query],
        StartTime=start_time,
        EndTime=end_time
    )

    # Extract and return the minimum CPU utilization
    min_utilization = min(response['MetricDataResults'][0]['Values'], default=0)
    return min_utilization

def get_all_instances(region):
    # Create EC2 client for the specified region
    ec2 = boto3.client('ec2', region_name=region)

    # Retrieve all running instances in the specified region
    instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    return instances['Reservations']

def generate_report():
    # Set the time range for the last two weeks and one month
    end_time = datetime.utcnow()
    start_time_two_weeks = end_time - timedelta(weeks=2)
    start_time_one_month = end_time - timedelta(days=30)

    # Get all AWS regions
    ec2_regions = [region['RegionName'] for region in boto3.client('ec2').describe_regions()['Regions']]

    # Create a list to store the report data
    report_data = []

    # Iterate through all regions
    for region in ec2_regions:
        # Get instances for the current region
        instances = get_all_instances(region)

        # Iterate through instances and retrieve information
        for reservation in instances:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_name = instance.get('Tags', [{}])[0].get('Value', 'N/A')
                instance_type = instance['InstanceType']

                # Retrieve minimum CPU utilization for the last two weeks
                min_cpu_utilization_two_weeks = get_min_cpu_utilization(instance_id, region, start_time_two_weeks, end_time)

                # Retrieve minimum CPU utilization for the last one month
                min_cpu_utilization_one_month = get_min_cpu_utilization(instance_id, region, start_time_one_month, end_time)

                # Append data to the report
                report_data.append({
                    'Region': region,
                    'InstanceName': instance_name,
                    'InstanceId': instance_id,
                    'InstanceType': instance_type,
                    'MinCPUUtilizationTwoWeeks': min_cpu_utilization_two_weeks,
                    'MinCPUUtilizationOneMonth': min_cpu_utilization_one_month
                })

    # Print the report
    print("Instance Report for Min CPU Utilization in All Regions:")
    for data in report_data:
        print(f"Region: {data['Region']}, Instance Name: {data['InstanceName']}, "
              f"Instance ID: {data['InstanceId']}, Instance Type: {data['InstanceType']}, "
              f"Min CPU Utilization (Last Two Weeks): {data['MinCPUUtilizationTwoWeeks']}%, "
              f"Min CPU Utilization (Last One Month): {data['MinCPUUtilizationOneMonth']}%")

if __name__ == "__main__":
    # Call the function to generate the report
    generate_report()

