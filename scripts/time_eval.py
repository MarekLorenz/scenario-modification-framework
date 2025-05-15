import numpy as np

# Read times from file
with open('times', 'r') as f:
    times = [float(line.strip()) for line in f.readlines()]

# Calculate statistics
median = np.median(times)
q1 = np.percentile(times, 25)
q3 = np.percentile(times, 75)
iqr = q3 - q1
lower_whisker = max(min(times), q1 - 1.5 * iqr)
upper_whisker = min(max(times), q3 + 1.5 * iqr)

# Find outliers
outliers = [t for t in times if t < lower_whisker or t > upper_whisker]

# Generate LaTeX boxplot data with exact format
print("\\addplot+[")
print("    boxplot prepared={")
print(f"        median={median:.4f},")
print(f"        upper quartile={q3:.4f},")
print(f"        lower quartile={q1:.4f},")
print(f"        upper whisker={upper_whisker:.4f},")
print(f"        lower whisker={lower_whisker:.4f},")
print(f"        upper notch={q3:.4f},")
print(f"        lower notch={q1:.4f}")
print("    },")
print("] coordinates {")
# Add outliers
for outlier in outliers:
    print(f"    (1,{outlier:.4f})")
print("};")