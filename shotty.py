import boto3
import click

session = boto3.Session()
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name': 'tag:Project', 'Values': [project]}]
        instances = ec2.instances.filter(Filter=filters)
    else:
        instances = ec2.instances.all()

    return instances

@click.group()
def cli():
    """"Shotty manages snapshots"""


@cli.group('snapshots')
def snapshots():
    """Commands for Snapshots"""

@snapshots.command('list')
@click.option('--project', default=None)
def list_snapshots(project):
    "List EC2 Snapshots"
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))

    return



@cli.group('volumes')
def volumes():
    """Commands for Volumes"""


@volumes.command('list')
@click.option('--project', default=None)
def list_volumes(project):
    "List EC2 Volumes"
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(" ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "Gib",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))

    return


@cli.group('instances')
def instances():
    """Commands for Instances"""

@instances.command('snapshot', help="Create snapshots of all volumes")
@click.option('--project', default=None, help="Only instances for project (tag Project:<name)")
def create_snapshots(project):
    "Create snapshots for EC2 Instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}....".format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by Snapshotalyer")
        print("Starting....{0}".format(i.id))
        i.start()
        i.wait_until_running()

    return


@instances.command('list')
@click.option('--project', default=None)
def list_instances(project):
    "List EC2 Instances"
    instances = filter_instances(project)
    for i in instances:
        tags =  { t['Key'] : t['Value'] for t in i.tags or [] }
        print(', '.join(
            (i.id,
             i.instance_type,
             i.placement['AvailabilityZone'],
             i.state['Name'],
             i.public_dns_name,
             tags.get('Project', '<no-project>')
        )
        )
        )

    return

@instances.command('stop')
@click.option('--project', default=None, help='Only Instances for Project')
def stop_instances(project):

    instances = filter_instances(project)

    for i in instances:
        print("Stopping.... {0}".format(i.id))
        i.stop()


@instances.command('start')
@click.option('--project', default=None, help='Only Instances for Project')
def stop_instances(project):

    instances = filter_instances(project)

    for i in instances:
        print("Starting.... {0}".format(i.id))
        i.start()


if __name__ == '__main__':
  cli()