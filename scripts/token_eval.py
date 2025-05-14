import numpy as np

# Read tokens from file
with open('tokens', 'r') as f:
    data = [line.strip().split(',') for line in f.readlines()]
    input_tokens = [int(x[0]) for x in data]
    output_tokens = [int(x[1]) for x in data]

# Calculate statistics for input tokens
input_median = np.median(input_tokens)
input_q1 = np.percentile(input_tokens, 25)
input_q3 = np.percentile(input_tokens, 75)
input_iqr = input_q3 - input_q1
input_lower_whisker = max(min(input_tokens), input_q1 - 1.5 * input_iqr)
input_upper_whisker = min(max(input_tokens), input_q3 + 1.5 * input_iqr)

# Calculate statistics for output tokens
output_median = np.median(output_tokens)
output_q1 = np.percentile(output_tokens, 25)
output_q3 = np.percentile(output_tokens, 75)
output_iqr = output_q3 - output_q1
output_lower_whisker = max(min(output_tokens), output_q1 - 1.5 * output_iqr)
output_upper_whisker = min(max(output_tokens), output_q3 + 1.5 * output_iqr)

print("\\begin{tikzpicture}")
print("\\begin{axis}[")
print("    width=0.8\\textwidth,")
print("    height=0.4\\textwidth,")
print("    xlabel={Input Tokens},")
print("    ylabel={Output Tokens},")
print("    scatter/classes={")
print("        a={mark=*,blue!50!black,mark size=2},")
print("        b={mark=*,red!50!black,mark size=2}")
print("    },")
print("    legend style={at={(0.5,-0.2)},anchor=north,legend columns=-1},")
print("    legend entries={Input-Output Tokens},")
print("    grid=major,")
print("    xmin=400,")
print("    xmax=2100,")
print("    ymin=20,")
print("    ymax=85")
print("]")

# Plot scatter points
for i, o in zip(input_tokens, output_tokens):
    print(f"\\addplot[scatter,only marks,scatter src=explicit symbolic]")
    print(f"    coordinates {{({i},{o}) [a]}};")

# Add trend line
z = np.polyfit(input_tokens, output_tokens, 1)
p = np.poly1d(z)
print("\\addplot[red,thick,no markers]")
print(f"    coordinates {{({min(input_tokens)},{p(min(input_tokens))}) ({max(input_tokens)},{p(max(input_tokens))})}};")

print("\\end{axis}")
print("\\end{tikzpicture}")

# Print statistics
print("\n% Statistics for Input Tokens")
print("\\begin{tikzpicture}")
print("\\begin{axis}[")
print("    width=0.8\\textwidth,")
print("    height=0.4\\textwidth,")
print("    boxplot prepared={")
print(f"        median={input_median:.1f},")
print(f"        upper quartile={input_q3:.1f},")
print(f"        lower quartile={input_q1:.1f},")
print(f"        upper whisker={input_upper_whisker:.1f},")
print(f"        lower whisker={input_lower_whisker:.1f}")
print("    },")
print("    xlabel={Input Tokens},")
print("    ytick=\\empty,")
print("    axis x line*=bottom,")
print("    axis y line*=left")
print("]")
print("\\addplot[boxplot prepared] coordinates {};")
print("\\end{axis}")
print("\\end{tikzpicture}")

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