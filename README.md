BASED ON THE WORK OF  
[Steffen-W]:https://github.com/Steffen-W/Convert_LTspice_to_Latex 

# Convert_LTspice_to_Latex
Convert LTspice to Latex (TikZ)

it works in linux and windows enviroments 

please eddit the paths acording to needs in the simpleRun.py script

## Setup
1. Install Python 3
2. Install LTspice
3. Latex packages: tikz, circuitikz, (amsmath)
 
## run it 
```
python3 simpleRun.py
```


# How to plot ltSpice bode diagrams in Latex
 * export to .txt 

 ```
%\pgfplotstableread[col sep=space]{IndividualFilters.txt}{\tableabcdef}
\begin{figure}[hbt!]
    \centering
    %\resizebox{\columnwidth}{!}{%
    \begin{tikzpicture}
        
        \begin{axis}[
                    xlabel=$f/Hz$, 
                    ylabel=$H/dB$, 
                    axis y line*=left,
                    xmode=log,
                    grid=both,
                    width=0.8\textwidth
                ]
                \addplot[color=blue] table [x index=0, y index=1, 
                        col sep=space,
                        %ignore chars={(,),\^^64,\^^42,\^^b0}, %0x64 = d, 0x42 = B, 0xB0=°
                        ignore chars={(,), \^^64  , \^^b0 , \ }, %0x64 = d, 0x42 = B, 0xB0=°
                        white space chars={\^^42}, %hotfix using 0x42 = B as white space to seperate data
                        %ignore chars={\^d},
                        %white space chars={(,)},
                        format=file
                        ]{schematics/IndividualFilters.txt};
                
        \end{axis}
        \begin{axis}[
                    xlabel=$f/Hz$, 
                    ylabel=$^\circ/deg$, 
                    ylabel near ticks, 
                    yticklabel pos=right,
                    %yticklabel pos=right,
                    %axis y line*=right,
                    xmode=log,
                    axis x line=none,
                    width=0.8\textwidth
                ]
                \addplot[color=red] table [x index=0, y index=3, 
                        col sep=space,
                        %ignore chars={(,),\^^64,\^^42,\^^b0}, %0x64 = d, 0x42 = B, 0xB0=°
                        ignore chars={(,), \^^64  , \^^b0 , \ }, %0x64 = d, 0x42 = B, 0xB0=°
                        white space chars={\^^42}, %hotfix using 0x42 = B as white space to seperate data
                        %ignore chars={\^d},
                        %white space chars={(,)},
                        format=file
                        ]{schematics/IndividualFilters.txt};
        \end{axis}
    \end{tikzpicture}
    %}
    \caption{Simulation of the filter in LTSpice}
    \label{fig:simulation_opamp}
\end{figure}
```