import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.patheffects as pe
from shark.eddy import Eddy, EddyMap

def profilTemperature(Tsurface, Tprofondeur, profondeurTfroid, Temp, distanceToCenter, Radius, amplitude):
    """Temp = Tprofondeur + (Tsurface - Tprofondeur) / (1 + np.exp(8 * depth / (profondeurTfroid + amplitude * 1e7 * 20 * np.exp(- distanceToCenter**2 / ((Radius / 3)* (1 + depth / profondeurTfroid) / 2)**2))))
    Temp - Tprofondeur = (Tsurface - Tprofondeur) / (1 + np.exp(8 * depth / (profondeurTfroid + amplitude * 1e7 * 20 * np.exp(- distanceToCenter**2 / ((Radius / 3)* (1 + depth / profondeurTfroid) / 2)**2)) - 4))
    np.exp(8 * depth / (profondeurTfroid + amplitude * 1e7 * 20 * np.exp(- distanceToCenter**2 / ((Radius / 3)* (1 + depth / profondeurTfroid) / 2)**2)) - 4) = ( Tsurface - Tprofondeur ) / ( Temp - Tprofondeur ) - 1
    depth / (profondeurTfroid + amplitude * 1e7 * 20 * np.exp(- distanceToCenter**2 / ((Radius / 3)* (1 + depth / profondeurTfroid) / 2)**2)) = (10 ** ((Tsurface - Tprofondeur ) / ( Temp - Tprofondeur ) - 1) + 4 ) / 8"""
    #depth = (profondeurTfroid + amplitude * 1e7 * 20 * np.exp(- distanceToCenter**2 / ((Radius / 3)* (1 + Tprofondeur / Tsurface) / 2)**2)) * (10 ** ((Tsurface - Tprofondeur ) / ( Temp - Tprofondeur ) - 1) + 4) / 8
    s = Radius / 2
    depth = (profondeurTfroid + amplitude * 1e7 * 30 * np.exp(- distanceToCenter**2 / (s* (1 + Tprofondeur / Temp) / 2)**2)) * (( np.log(((Tsurface - Tprofondeur ) / ( Temp - Tprofondeur ) - 1)) + 4) / 8)
    return depth

def settingUp(eddy: Eddy, Tsurface = 20.2, Tprofondeur = 10, profondeurTfroid = 900):
    Radius = eddy.radius
    amplitude = eddy.amplitude

    distanceToCenter = np.linspace(-Radius, Radius, 100)
    Temps = np.arange(Tprofondeur, Tsurface)
    depths = np.array([profilTemperature(Tsurface, Tprofondeur, profondeurTfroid, Temp, distanceToCenter, Radius, amplitude) for Temp in Temps])
    return distanceToCenter, Temps, depths

# Affichage généré en partie par IA

def contiguous_segments(idx):
    """Retourne [(start,end),...] pour indices contigus dans idx (idx = array d'indices triés)."""
    if len(idx) == 0:
        return []
    segs = []
    start = idx[0]
    prev = idx[0]
    for k in idx[1:]:
        if k == prev + 1:
            prev = k
            continue
        segs.append((start, prev))
        start = k
        prev = k
    segs.append((start, prev))
    return segs

def affiche(depths, Temps, distanceToCenter, Radius):
    # --- inputs attendus (existant dans ton script) ---
    # depths: shape (nTemps, nDist) ; depths[i,j] = profondeur pour Temps[i] à distance j
    # Temps: array de températures (ex. np.arange(11,21))
    # distanceToCenter: array de positions (ex. np.linspace(-Radius, Radius, N))
    # Radius: scalaire

    # Normalisation abscisse
    X = distanceToCenter / Radius

    # trier températures en croissant et réordonner depths
    inds = np.argsort(Temps)
    Temps_asc = Temps[inds]
    depths_asc = depths[inds, :]

    # colormap / normalisation
    cmap = cm.get_cmap('coolwarm')
    norm = colors.Normalize(vmin=Temps_asc.min(), vmax=Temps_asc.max())

    fig, ax = plt.subplots(figsize=(10, 6))

    nT, nX = depths_asc.shape
    # profondeur max utile pour la bande "bottom"
    finite_mask = np.isfinite(depths_asc)
    if finite_mask.any():
        max_depth = np.nanmax(depths_asc[finite_mask])
    else:
        max_depth = 1.0

    # --- 1) bandes intérieures entre T_i et T_{i+1} ---
    for i in range(nT - 1):
        depth_low = depths_asc[i, :]
        depth_high = depths_asc[i + 1, :]
        T_mid = 0.5 * (Temps_asc[i] + Temps_asc[i + 1])
        color = cmap(norm(T_mid))

        valid = np.isfinite(depth_low) & np.isfinite(depth_high)
        valid_idx = np.where(valid)[0]
        for (s, e) in contiguous_segments(valid_idx):
            xi = X[s:e+1]
            y1 = depth_low[s:e+1]
            y2 = depth_high[s:e+1]
            ax.fill_between(xi, y1, y2, facecolor=color, edgecolor=None, linewidth=0, zorder=1)

    # --- 2) bande au-dessus de la plus chaude (surface -> isotherme la plus chaude) ---
    surface = np.zeros_like(X)
    depth_warmest = depths_asc[-1, :]
    # couleur en dehors: prendre le midpoint au dessus de la plus haute temperature
    if nT > 1:
        step_up = Temps_asc[-1] - Temps_asc[-2]
    else:
        step_up = 1.0
    T_mid_top = Temps_asc[-1] + 0.5 * step_up
    color_top = cmap(norm(T_mid_top))

    valid = np.isfinite(depth_warmest)
    valid_idx = np.where(valid)[0]
    for (s, e) in contiguous_segments(valid_idx):
        xi = X[s:e+1]
        y1 = surface[s:e+1]
        y2 = depth_warmest[s:e+1]
        ax.fill_between(xi, y1, y2, facecolor=color_top, edgecolor=None, linewidth=0, zorder=1)

    # --- 3) bande sous la plus froide (isotherme la plus froide -> bottom) ---
    depth_coldest = depths_asc[0, :]
    bottom_depth = np.full_like(X, max_depth)
    if nT > 1:
        step_down = Temps_asc[1] - Temps_asc[0]
    else:
        step_down = 1.0
    T_mid_bot = Temps_asc[0] - 0.5 * step_down
    color_bot = cmap(norm(T_mid_bot))

    valid = np.isfinite(depth_coldest)
    valid_idx = np.where(valid)[0]
    for (s, e) in contiguous_segments(valid_idx):
        xi = X[s:e+1]
        y1 = depth_coldest[s:e+1]
        y2 = bottom_depth[s:e+1]
        ax.fill_between(xi, y1, y2, facecolor=color_bot, edgecolor=None, linewidth=0, zorder=1)

    # --- 4) tracer toutes les isothermes par segments (au-dessus du remplissage) ---
    for i, Tval in enumerate(Temps_asc):
        dline = depths_asc[i, :]
        valid_idx = np.where(np.isfinite(dline))[0]
        for (s, e) in contiguous_segments(valid_idx):
            xi = X[s:e+1]
            yi = dline[s:e+1]
            line, = ax.plot(xi, yi, color='black', linewidth=1.8, zorder=10)
            # halo blanc pour lisibilité sur n'importe quel fond
            line.set_path_effects([pe.Stroke(linewidth=3.5, foreground='white', alpha=0.9),
                                pe.Normal()])

    # --- 5) annotations (à droite) : placer label à la colonne la plus à droite valide pour chaque isotherme ---
    x_annot = 0.98
    j_annot = np.argmin(np.abs(X - x_annot))
    for i, Tval in enumerate(Temps_asc):
        # si la colonne j_annot n'est pas valide, chercher la colonne valide la plus proche vers la gauche
        dcol = depths_asc[i, :]
        if np.isfinite(dcol[j_annot]):
            ylab = dcol[j_annot]
            xpos = x_annot
        else:
            # trouver index valide le plus proche de j_annot
            valid = np.where(np.isfinite(dcol))[0]
            if valid.size == 0:
                continue
            # choisir le plus proche en distance horizontale
            jnear = valid[np.argmin(np.abs(valid - j_annot))]
            ylab = dcol[jnear]
            xpos = X[jnear] + 0.01  # petite marge
        ax.text(xpos, ylab, f" {float(Tval):.0f}°C", va='center', ha='left',
                fontsize=9, color='white', bbox=dict(facecolor='black', alpha=0.5, pad=1), zorder=20)

    # esthétique
    ax.invert_yaxis()
    ax.set_xlabel("Distance à l'épicentre normalisée")
    ax.set_ylabel("Profondeur (m)")
    ax.set_title("Isothermes de température sous le vortex ")

    # colorbar basée sur la colormap et la gamme de températures
    mappable = cm.ScalarMappable(cmap=cmap, norm=norm)
    mappable.set_array(Temps_asc)
    cbar = fig.colorbar(mappable, ax=ax)
    cbar.set_label("Température (°C)")

    plt.tight_layout()
    plt.savefig("GradientTemperature.png")
    plt.show()
    return

def envoiImage(eddy: Eddy):
    distanceToCenter, Temps, depths = settingUp(eddy)
    affiche(depths, Temps, distanceToCenter, eddy.radius)