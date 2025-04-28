import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# Global deque for storing the last 50 expected profit values
expected_profit_data = deque(maxlen=50)

# Set up the plot
fig, ax = plt.subplots()
ax.set_title('Live Expected Profit from Refining')
ax.set_xlabel('Time (Ticks)')
ax.set_ylabel('Expected Profit ($)')
line, = ax.plot([], [], lw=2)

# Initialize the plot's limits
ax.set_xlim(0, 100)  # Default initial range, will be updated later
ax.set_ylim(-100_000, 500_000)  # Adjust y-axis as needed

def update_plot(frame):
    """
    Update the plot with the latest expected profit data.
    """
    x_data = range(len(expected_profit_data))
    y_data = list(expected_profit_data)

    line.set_data(x_data, y_data)
    return line,

def refining_expected_profit(profit):
    """
    Add new expected profit value to the visualization.
    """
    expected_profit_data.append(profit)

def run_live_dashboard():
    """
    Run the live dashboard to plot expected profits.
    """
    ani = animation.FuncAnimation(fig, update_plot, interval=1000)
    plt.show()
