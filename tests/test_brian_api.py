
import brian2 as b2
from brian2 import Section, um

try:
    s = Section(n=1, length=[10]*um, diameter=[1,1]*um)
    d = Section(n=1, length=[10]*um, diameter=[1,1]*um)
    print("Sections created.")
    
    if hasattr(s, "append"):
        print("Section has append method.")
        s.append(d)
        print("Append successful.")
    else:
        print("Section has NO append method.")
        print(dir(s))
        
except Exception as e:
    print(f"Error: {e}")
