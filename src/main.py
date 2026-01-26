"""
Multi-Agent Virtual Company - CLI Entry Point.

This module provides a command-line interface for running
research queries through the multi-agent workflow.

Usage:
    python -m src.main "Your research query here"
    python -m src.main --help
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None):
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logging
    """
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )
    
    # File handler (if specified)
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
        )


def run_research(
    query: str,
    max_iterations: int = 3,
    output_dir: Optional[Path] = None,
    save_report: bool = True,
) -> dict:
    """
    Run a research query through the multi-agent workflow.
    
    Args:
        query: Research query/topic
        max_iterations: Maximum revision iterations
        output_dir: Directory to save reports
        save_report: Whether to save the report to file
        
    Returns:
        Dictionary with workflow results
    """
    from config.settings import settings
    from src.graph import create_runner, get_state_summary
    
    logger.info("=" * 60)
    logger.info("MULTI-AGENT VIRTUAL COMPANY")
    logger.info("=" * 60)
    logger.info(f"Query: {query}")
    logger.info(f"Max Iterations: {max_iterations}")
    logger.info("-" * 60)
    
    # Create and run workflow
    runner = create_runner(
        api_key=settings.groq_api_key,
        tavily_api_key=settings.tavily_api_key,
        max_iterations=max_iterations,
        enable_checkpointing=True,
    )
    
    # Run the workflow
    start_time = datetime.now()
    result = runner.run(query)
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    
    # Get summary
    summary = get_state_summary(result)
    
    logger.info("=" * 60)
    logger.info("WORKFLOW RESULTS")
    logger.info("=" * 60)
    logger.info(f"Status: {summary['status']}")
    logger.info(f"Iterations: {summary['iteration']}")
    logger.info(f"Duration: {duration:.2f} seconds")
    logger.info(f"Has Report: {summary['has_report']}")
    
    if summary['error']:
        logger.error(f"Error: {summary['error']}")
    
    # Save report if available
    if save_report and result.get("final_report"):
        output_path = save_final_report(
            result["final_report"],
            query,
            output_dir or Path("outputs"),
        )
        logger.info(f"Report saved to: {output_path}")
    
    return {
        "status": summary["status"],
        "duration": duration,
        "iterations": summary["iteration"],
        "has_report": summary["has_report"],
        "error": summary.get("error"),
        "result": result,
    }


def save_final_report(report, query: str, output_dir: Path) -> Path:
    """
    Save the final report to a file.
    
    Args:
        report: FinalReport object
        query: Original query (for filename)
        output_dir: Directory to save report
        
    Returns:
        Path to saved report
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename from query
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = "".join(c if c.isalnum() or c == " " else "_" for c in query[:50])
    safe_query = safe_query.replace(" ", "_").lower()
    filename = f"report_{timestamp}_{safe_query}.md"
    
    output_path = output_dir / filename
    
    # Convert report to markdown
    if hasattr(report, "to_markdown"):
        content = report.to_markdown()
    else:
        # Fallback: convert to string
        content = str(report)
    
    output_path.write_text(content, encoding="utf-8")
    
    return output_path


def print_report(result: dict):
    """
    Print the final report to console.
    
    Args:
        result: Workflow result dictionary
    """
    report = result.get("result", {}).get("final_report")
    
    if not report:
        print("\nNo report generated.")
        return
    
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    
    if hasattr(report, "title"):
        print(f"\nTitle: {report.title}")
    
    if hasattr(report, "executive_summary"):
        print(f"\nExecutive Summary:\n{report.executive_summary}")
    
    if hasattr(report, "sections"):
        for i, section in enumerate(report.sections, 1):
            print(f"\n--- Section {i}: {section.title} ---")
            print(section.content[:500] + "..." if len(section.content) > 500 else section.content)
    
    if hasattr(report, "conclusion"):
        print(f"\nConclusion:\n{report.conclusion}")
    
    print("\n" + "=" * 60)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Virtual Company - AI Research System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main "Latest trends in AI agents"
  python -m src.main "Impact of quantum computing on cryptography" --iterations 5
  python -m src.main "Climate change solutions 2025" --output ./reports --verbose
        """,
    )
    
    parser.add_argument(
        "query",
        type=str,
        help="Research query or topic to investigate",
    )
    
    parser.add_argument(
        "--iterations", "-i",
        type=int,
        default=3,
        help="Maximum revision iterations (default: 3)",
    )
    
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("outputs"),
        help="Output directory for reports (default: ./outputs)",
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save the report to file",
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    
    parser.add_argument(
        "--print-report", "-p",
        action="store_true",
        help="Print the full report to console",
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    try:
        # Check configuration
        from config.settings import settings
        if settings is None:
            logger.error("Configuration not loaded. Please check your .env file.")
            sys.exit(1)
        
        # Run the research workflow
        result = run_research(
            query=args.query,
            max_iterations=args.iterations,
            output_dir=args.output,
            save_report=not args.no_save,
        )
        
        # Print report if requested
        if args.print_report:
            print_report(result)
        
        # Exit with appropriate code
        if result["status"] == "completed":
            logger.info("Research completed successfully!")
            sys.exit(0)
        else:
            logger.error(f"Research failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
