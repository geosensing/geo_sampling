"""Modern command-line interface for geo_sampling."""

import sys
from typing import Optional

import click

from . import __version__
from .extractor import RoadExtractor
from .sampler import RoadSampler, load_segments_from_csv
from .convenience import sample_roads_for_region, get_road_summary


@click.group()
@click.version_option(version=__version__)
def cli():
    """geo_sampling: Extract and sample road segments from OpenStreetMap data.

    This tool helps you randomly sample street locations for data collection
    by downloading OpenStreetMap data and processing road segments.
    """
    pass


@cli.command()
@click.argument("country")
@click.argument("region")
@click.option(
    "--admin-level", "-l", default=1, type=int, help="Administrative level (1-4)"
)
@click.option(
    "--road-types",
    "-t",
    multiple=True,
    help="Road types to include (can be specified multiple times)",
)
@click.option("--output", "-o", default="roads.csv", help="Output CSV file")
@click.option(
    "--segment-length", "-d", default=500, type=int, help="Segment length in meters"
)
@click.option("--plot", is_flag=True, help="Show plot of extracted roads")
@click.option("--data-dir", default="data", help="Directory for cached data")
def extract(
    country: str,
    region: str,
    admin_level: int,
    road_types: tuple,
    output: str,
    segment_length: int,
    plot: bool,
    data_dir: str,
):
    """Extract road segments for a geographic region.

    Downloads administrative boundaries and OpenStreetMap data, then extracts
    road segments split into specified lengths.

    Examples:

        geo-sampling extract "India" "NCT of Delhi" --output delhi_roads.csv

        geo-sampling extract "Thailand" "Trang" -t primary -t secondary --plot
    """
    click.echo(f"Extracting roads for {region}, {country}...")

    # Convert road types tuple to list (None if empty)
    road_type_list = list(road_types) if road_types else None

    try:
        extractor = RoadExtractor(country, region, admin_level, data_dir)
        segments = extractor.get_roads(road_type_list, segment_length)

        # Save to CSV
        extractor.save_csv(output, road_type_list, segment_length)
        click.echo(f"✓ Extracted {len(segments)} segments")

        # Show summary
        road_summary = {}
        for segment in segments:
            road_summary[segment.osm_type] = road_summary.get(segment.osm_type, 0) + 1

        click.echo("Road type summary:")
        for road_type, count in sorted(road_summary.items()):
            click.echo(f"  {road_type}: {count}")

        # Plot if requested
        if plot:
            click.echo("Showing plot...")
            extractor.plot(road_type_list, segment_length)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--sample-size", "-n", type=int, required=True, help="Number of segments to sample"
)
@click.option("--road-types", "-t", multiple=True, help="Road types to include")
@click.option("--output", "-o", default="sample.csv", help="Output CSV file")
@click.option(
    "--strategy",
    default="random",
    type=click.Choice(["random", "stratified"]),
    help="Sampling strategy",
)
@click.option("--seed", "-s", type=int, help="Random seed for reproducibility")
@click.option("--plot", is_flag=True, help="Show plot of sampled roads")
def sample(
    input_file: str,
    sample_size: int,
    road_types: tuple,
    output: str,
    strategy: str,
    seed: Optional[int],
    plot: bool,
):
    """Sample road segments from an extracted dataset.

    Takes a CSV file of extracted road segments and creates a random or
    stratified sample.

    Examples:

        geo-sampling sample roads.csv -n 1000 --output sample.csv

        geo-sampling sample roads.csv -n 500 -t primary -t secondary --plot
    """
    click.echo(f"Loading segments from {input_file}...")

    try:
        # Load segments
        segments = load_segments_from_csv(input_file)
        click.echo(f"Loaded {len(segments)} segments")

        # Create sampler
        sampler = RoadSampler(segments)

        # Filter by road types if specified
        road_type_list = list(road_types) if road_types else None

        # Sample
        click.echo(f"Creating {strategy} sample of {sample_size} segments...")

        if strategy == "random":
            sample_segments = sampler.random_sample(sample_size, road_type_list, seed)
        else:  # stratified
            sample_segments = sampler.stratified_sample(
                sample_size, road_types=road_type_list, seed=seed
            )

        # Save sample
        sampler.save_csv(sample_segments, output)
        click.echo(f"✓ Saved {len(sample_segments)} segments to {output}")

        # Show summary
        road_summary = sampler.get_road_type_summary()
        sample_summary = {}
        for segment in sample_segments:
            sample_summary[segment.osm_type] = (
                sample_summary.get(segment.osm_type, 0) + 1
            )

        click.echo("Sample summary:")
        for road_type in sorted(road_summary.keys()):
            original_count = road_summary[road_type]
            sample_count = sample_summary.get(road_type, 0)
            percentage = (
                (sample_count / original_count * 100) if original_count > 0 else 0
            )
            click.echo(
                f"  {road_type}: {sample_count}/{original_count} ({percentage:.1f}%)"
            )

        # Plot if requested
        if plot:
            click.echo("Showing plot...")
            sampler.plot_sample(sample_segments)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("country")
@click.argument("region")
@click.option(
    "--sample-size", "-n", type=int, required=True, help="Number of segments to sample"
)
@click.option(
    "--admin-level", "-l", default=1, type=int, help="Administrative level (1-4)"
)
@click.option("--road-types", "-t", multiple=True, help="Road types to include")
@click.option("--output", "-o", default="workflow_sample.csv", help="Output CSV file")
@click.option(
    "--segment-length", "-d", default=500, type=int, help="Segment length in meters"
)
@click.option(
    "--strategy",
    default="random",
    type=click.Choice(["random", "stratified"]),
    help="Sampling strategy",
)
@click.option("--seed", "-s", type=int, help="Random seed for reproducibility")
@click.option("--plot", is_flag=True, help="Show plot of results")
@click.option("--data-dir", default="data", help="Directory for cached data")
def workflow(
    country: str,
    region: str,
    sample_size: int,
    admin_level: int,
    road_types: tuple,
    output: str,
    segment_length: int,
    strategy: str,
    seed: Optional[int],
    plot: bool,
    data_dir: str,
):
    """Complete workflow: extract roads and create sample in one step.

    This command combines extraction and sampling into a single operation,
    which is convenient for most use cases.

    Examples:

        geo-sampling workflow "India" "NCT of Delhi" -n 1000 --plot

        geo-sampling workflow "Thailand" "Bangkok" -n 500 -t primary -t trunk
    """
    click.echo(f"Running complete workflow for {region}, {country}...")
    click.echo(f"Target sample size: {sample_size}")

    try:
        # Convert road types
        road_type_list = list(road_types) if road_types else None

        # Run workflow
        sample_segments = sample_roads_for_region(
            country,
            region,
            sample_size,
            admin_level,
            road_type_list,
            segment_length,
            strategy,
            seed,
            data_dir,
        )

        # Save results
        sampler = RoadSampler(sample_segments)
        sampler.save_csv(sample_segments, output)
        click.echo(f"✓ Saved {len(sample_segments)} segments to {output}")

        # Show summary
        road_summary = sampler.get_road_type_summary()
        click.echo("Sample summary:")
        for road_type, count in sorted(road_summary.items()):
            click.echo(f"  {road_type}: {count}")

        # Plot if requested
        if plot:
            click.echo("Showing plot...")
            sampler.plot_sample(sample_segments, show_comparison=False)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("country")
@click.argument("region")
@click.option(
    "--admin-level", "-l", default=1, type=int, help="Administrative level (1-4)"
)
@click.option("--data-dir", default="data", help="Directory for cached data")
def info(country: str, region: str, admin_level: int, data_dir: str):
    """Show information about roads in a region.

    Extracts road data and displays summary statistics without saving files.

    Examples:

        geo-sampling info "India" "NCT of Delhi"

        geo-sampling info "Thailand" "Bangkok" --admin-level 2
    """
    click.echo(f"Getting road information for {region}, {country}...")

    try:
        summary = get_road_summary(country, region, admin_level, data_dir)

        click.echo(f"\n📍 Region: {summary['region']}")
        click.echo(f"📊 Total segments: {summary['total_segments']:,}")
        click.echo(f"🛣️  Road types found: {len(summary['road_types'])}")

        click.echo("\n📈 Breakdown by road type:")
        total = summary["total_segments"]
        for road_type, count in sorted(
            summary["road_type_counts"].items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / total * 100) if total > 0 else 0
            click.echo(f"  {road_type:<15} {count:>6,} ({percentage:>5.1f}%)")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
