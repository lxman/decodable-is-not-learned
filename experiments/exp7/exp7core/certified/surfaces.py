"""Only the legacy-surface renderer; no item constructors/generation API."""
def shape_path(points, decimals=False):
    pt = (lambda p: f'{p[0]:.2f},{p[1]:.2f}') if decimals else (lambda p: f'{p[0]},{p[1]}')
    return 'M '+pt(points[0])+' '+' '.join('L '+pt(p) for p in points[1:]+points[:1])


def bb_surfaces(family, facts):
    out = []
    for f in facts:
        if family == 'words':
            out.append(f"The word {f['scrambled']} is a scrambled version of the English word ")
        elif family == 'deduction':
            parts = [('an ' if c[0] in 'aeiou' else 'a ')+c+' book' for c in f['listed']]
            intro = 'On a shelf, there are five books: '+', '.join(parts[:-1])+', and '+parts[-1]+'.'
            lines = [line.replace('before', 'to the left of').replace('after', 'to the right of') for line in f['clue_lines']]
            out.append(' '.join([intro, *lines]))
        elif family == 'units':
            n, p, Q = (f['roles'][k] for k in ('n','p','Q'))
            out.append(f'A bell rings {n} times every {p} hours. It will ring {Q} times in () hours.')
        else:
            out.append(f'This SVG path element <path d="{f["path"]}"/> draws a ')
            pts = [[int(x),int(y)] for x,y in f['points']]
            out.append(f'This SVG path element <path d="{shape_path(pts, True)}"/> draws a ')
    return out
