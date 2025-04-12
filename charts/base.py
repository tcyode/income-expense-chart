# charts/base.py
# Base class for chart generation

import matplotlib.pyplot as plt

class BaseChart:
    """Base class for all chart types."""
    
    def __init__(self, title=None, xlabel=None, ylabel=None, figsize=(15, 8)):
        """Initialize chart with basic properties."""
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.figsize = figsize
        self.fig = None
        self.ax = None
    
    def create_figure(self):
        """Create the matplotlib figure and axis."""
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        return self.fig, self.ax
    
    def add_styling(self):
        """Add basic styling to the chart."""
        if self.title:
            self.ax.set_title(self.title)
        if self.xlabel:
            self.ax.set_xlabel(self.xlabel)
        if self.ylabel:
            self.ax.set_ylabel(self.ylabel)
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    def save_chart(self, filename, dpi=300):
        """Save the chart to a file."""
        self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    
    def show_chart(self):
        """Display the chart."""
        plt.tight_layout()
        plt.show()
    
    def plot(self, data):
        """Abstract method to be implemented by child classes."""
        raise NotImplementedError("Subclasses must implement plot()")
