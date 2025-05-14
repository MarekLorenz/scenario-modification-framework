import numpy as np

# Read tokens from file
with open('tokens', 'r') as f:
    output_tokens = [int(line.strip()) for line in f.readlines()]

# Calculate statistics for output tokens
output_median = np.median(output_tokens)
output_q1 = np.percentile(output_tokens, 25)
output_q3 = np.percentile(output_tokens, 75)
output_iqr = output_q3 - output_q1
output_lower_whisker = max(min(output_tokens), output_q1 - 1.5 * output_iqr)
output_upper_whisker = min(max(output_tokens), output_q3 + 1.5 * output_iqr)

print("\n% Statistics for Output Tokens")
print("\\begin{tikzpicture}")
print("\\begin{axis}[")
print("    width=0.8\\textwidth,")
print("    height=0.4\\textwidth,")
print("    boxplot prepared={")
print(f"        median={output_median:.1f},")
print(f"        upper quartile={output_q3:.1f},")
print(f"        lower quartile={output_q1:.1f},")
print(f"        upper whisker={output_upper_whisker:.1f},")
print(f"        lower whisker={output_lower_whisker:.1f}")
print("    },")
print("    xlabel={Output Tokens},")
print("    ytick=\\empty,")
print("    axis x line*=bottom,")
print("    axis y line*=left")
print("]")
print("\\addplot[boxplot prepared] coordinates {};")
print("\\end{axis}")
print("\\end{tikzpicture}")