"""
Medical Data Visualizer for creating interactive charts from medical JSON data.

This module provides functionality to create various types of visualizations
for medical test results and patient data.
"""

import json
import logging
from typing import Any, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Python 3.12+ type aliases
type MedicalData = dict[str, Any]
type ObservationList = list[dict[str, Any]]
type VisualizationDict = dict[str, go.Figure]

logger = logging.getLogger(__name__)


class MedicalDataVisualizer:
    """
    A visualizer for creating interactive charts from medical JSON data.
    
    This class handles the creation of various chart types including gauge charts,
    bar charts, and trend analysis for medical test results.
    """
    
    def __init__(self):
        """Initialize the Medical Data Visualizer."""
        logger.info("Medical Data Visualizer initialized")
    
    def create_visualizations(self, medical_data: MedicalData) -> VisualizationDict:
        """
        Create comprehensive visualizations from medical data.
        
        Args:
            medical_data (Dict[str, Any]): Structured medical data
            
        Returns:
            Dict[str, go.Figure]: Dictionary of visualization figures
        """
        try:
            visualizations = {}
            
            if 'observations' not in medical_data or not medical_data['observations']:
                logger.warning("No observations found in medical data")
                return visualizations
            
            observations = medical_data['observations']
            
            # Create individual test visualizations
            for i, obs in enumerate(observations):
                test_name = obs.get('test_name', f'Test_{i+1}')
                
                # Create gauge chart for each test
                gauge_fig = self._create_gauge_chart(obs)
                if gauge_fig:
                    visualizations[f"{test_name}_gauge"] = gauge_fig
            
            # Create overview charts
            overview_charts = self._create_overview_charts(observations)
            visualizations.update(overview_charts)
            
            logger.info(f"Created {len(visualizations)} visualizations")
            return visualizations
            
        except Exception as e:
            logger.error(f"Failed to create visualizations: {str(e)}")
            return {}
    
    def _create_gauge_chart(self, observation: dict[str, Any]) -> Optional[go.Figure]:
        """
        Create a gauge chart for a single test observation.
        
        Args:
            observation (Dict[str, Any]): Single test observation data
            
        Returns:
            Optional[go.Figure]: Gauge chart figure or None if creation fails
        """
        try:
            test_name = observation.get('test_name', 'Unknown Test')
            result = observation.get('result', '0')
            unit = observation.get('unit', '')
            reference_range = observation.get('reference_range', '')
            flag = observation.get('flag', 'N')
            
            # Parse numeric result
            try:
                numeric_result = float(result)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse numeric result for {test_name}: {result}")
                return None
            
            # Parse reference range
            range_min, range_max = self._parse_reference_range(reference_range)
            if range_min is None or range_max is None:
                logger.warning(f"Could not parse reference range for {test_name}: {reference_range}")
                return None
            
            # Determine gauge color based on flag
            color = self._get_flag_color(flag)
            
            # Create gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=numeric_result,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"{test_name}<br><span style='font-size:0.8em;color:gray'>{unit}</span>"},
                delta={'reference': (range_min + range_max) / 2},
                gauge={
                    'axis': {'range': [None, max(range_max * 1.2, numeric_result * 1.2)]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, range_min], 'color': "lightgray"},
                        {'range': [range_min, range_max], 'color': "lightgreen"},
                        {'range': [range_max, max(range_max * 1.2, numeric_result * 1.2)], 'color': "lightgray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': numeric_result
                    }
                }
            ))
            
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=60, b=20),
                font={'size': 12}
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create gauge chart: {str(e)}")
            return None
    
    def _create_overview_charts(self, observations: ObservationList) -> VisualizationDict:
        """
        Create overview charts for all observations.
        
        Args:
            observations (List[Dict[str, Any]]): List of all test observations
            
        Returns:
            Dict[str, go.Figure]: Dictionary of overview chart figures
        """
        charts = {}
        
        try:
            # Prepare data for overview charts
            test_names = []
            results = []
            flags = []
            units = []
            
            for obs in observations:
                test_name = obs.get('test_name', 'Unknown')
                result = obs.get('result', '0')
                flag = obs.get('flag', 'N')
                unit = obs.get('unit', '')
                
                try:
                    numeric_result = float(result)
                    test_names.append(test_name)
                    results.append(numeric_result)
                    flags.append(flag)
                    units.append(unit)
                except (ValueError, TypeError):
                    continue
            
            if not test_names:
                return charts
            
            # Create bar chart of all results
            colors = [self._get_flag_color(flag) for flag in flags]
            
            bar_fig = go.Figure(data=[
                go.Bar(
                    x=test_names,
                    y=results,
                    marker_color=colors,
                    text=[f"{result} {unit}" for result, unit in zip(results, units)],
                    textposition='auto',
                )
            ])
            
            bar_fig.update_layout(
                title="All Test Results Overview",
                xaxis_title="Tests",
                yaxis_title="Results",
                height=400,
                margin=dict(l=20, r=20, t=60, b=100),
                xaxis={'tickangle': 45}
            )
            
            charts['overview_bar'] = bar_fig
            
            # Create flag distribution pie chart
            flag_counts = {}
            for flag in flags:
                flag_name = self._get_flag_name(flag)
                flag_counts[flag_name] = flag_counts.get(flag_name, 0) + 1
            
            if len(flag_counts) > 1:
                pie_fig = go.Figure(data=[
                    go.Pie(
                        labels=list(flag_counts.keys()),
                        values=list(flag_counts.values()),
                        hole=0.3,
                        marker_colors=[self._get_flag_color(self._get_flag_code(name)) for name in flag_counts.keys()]
                    )
                ])
                
                pie_fig.update_layout(
                    title="Test Results Distribution",
                    height=400,
                    margin=dict(l=20, r=20, t=60, b=20)
                )
                
                charts['flag_distribution'] = pie_fig
            
        except Exception as e:
            logger.error(f"Failed to create overview charts: {str(e)}")
        
        return charts
    
    def _parse_reference_range(self, reference_range: str) -> tuple[Optional[float], Optional[float]]:
        """
        Parse reference range string into min and max values.
        
        Args:
            reference_range (str): Reference range string (e.g., "12.0-16.0")
            
        Returns:
            Tuple[Optional[float], Optional[float]]: Min and max values or (None, None)
        """
        try:
            if '-' in reference_range:
                parts = reference_range.split('-')
                if len(parts) == 2:
                    range_min = float(parts[0].strip())
                    range_max = float(parts[1].strip())
                    return range_min, range_max
        except (ValueError, AttributeError):
            pass
        
        return None, None
    
    def _get_flag_color(self, flag: str) -> str:
        """
        Get color based on test result flag.
        
        Args:
            flag (str): Test result flag ('N', 'H', 'L', etc.)
            
        Returns:
            str: Color string
        """
        flag_colors = {
            'N': '#28a745',  # Green for normal
            'H': '#dc3545',  # Red for high
            'L': '#ffc107',  # Yellow for low
            'C': '#17a2b8',  # Blue for critical
        }
        return flag_colors.get(flag.upper(), '#6c757d')  # Gray for unknown
    
    def _get_flag_name(self, flag: str) -> str:
        """
        Get human-readable name for flag.
        
        Args:
            flag (str): Test result flag
            
        Returns:
            str: Human-readable flag name
        """
        flag_names = {
            'N': 'Normal',
            'H': 'High',
            'L': 'Low',
            'C': 'Critical'
        }
        return flag_names.get(flag.upper(), 'Unknown')
    
    def _get_flag_code(self, flag_name: str) -> str:
        """
        Get flag code from human-readable name.
        
        Args:
            flag_name (str): Human-readable flag name
            
        Returns:
            str: Flag code
        """
        name_to_code = {
            'Normal': 'N',
            'High': 'H',
            'Low': 'L',
            'Critical': 'C'
        }
        return name_to_code.get(flag_name, 'N')