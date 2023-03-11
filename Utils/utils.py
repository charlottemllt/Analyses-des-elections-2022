import pandas as pd

def preprocess(df):
    depart = 21
    listeColonnes = df.columns.to_list()
    liste = ['N°Panneau', 'Sexe', 'Nom', 'Prénom', 'Voix', '% Voix/Ins', '% Voix/Exp']
    for index in range(12):
        Nom = df[listeColonnes[7*index + 2 + depart]].iloc[0]
        Prenom = df[listeColonnes[7*index + 3 + depart]].iloc[0]
        for i in range(7):
            listeColonnes[7*index + i + depart] = (liste[i] + ' ' + Prenom + ' ' + Nom)
    df.columns = listeColonnes

    colonnesAGarder = ['Libellé du département', 'Code de la circonscription', 'Libellé de la circonscription',
                       'Inscrits', 'Abstentions', 'Votants', 'Blancs', 'Nuls', 'Exprimés']
    for col in df.columns:
        if 'Voix ' in col:
            colonnesAGarder.append(col)

    df = df[colonnesAGarder]

    for i in range(df.shape[1]):
        if 'Voix ' in colonnesAGarder[i]:
            colonnesAGarder[i] = colonnesAGarder[i][5:]
    df.columns = colonnesAGarder

    df['ind'] = df.apply(lambda x: x['Libellé du département'] + str(x['Code de la circonscription']), axis=1)
    df = df.groupby('ind').sum()

    return df


def arrives_en_tete(df_, alliances=False):
    df = preprocess(df_)

    if alliances:
        df['NUPES'] = (df['Fabien ROUSSEL'] + df['Jean-Luc MÉLENCHON']
                       + df['Yannick JADOT'] + df['Anne HIDALGO'])
        df['Ext_Droite'] = (df['Marine LE PEN'] + df['Nicolas DUPONT-AIGNAN'])
        df = df.rename(columns={'Emmanuel MACRON': 'LREM'})
        df.drop(['Fabien ROUSSEL', 'Jean-Luc MÉLENCHON', 'Yannick JADOT', 'Anne HIDALGO',
                 'Marine LE PEN', 'Nicolas DUPONT-AIGNAN'], axis=1, inplace=True)

    for i in range(7, df.shape[1]):
        col = df.columns[i]
        df[col + ' (% des Inscrits)'] = (df[col] * 100 / df['Inscrits'])
        df[col] = (df[col] * 100 / df['Exprimés'])

    df.drop(['Code de la circonscription', 'Inscrits', 'Abstentions',
                  'Votants', 'Blancs', 'Nuls', 'Exprimés'], axis=1, inplace=True)

    df['Arrivé(e) en tête'] = pd.Series()
    data = df.iloc[:, :-1].values
    stop = alliances*8 + (1-alliances) *12
    for i in range(df.shape[0]):
        amax = data[i, :stop].argmax()
        col = amax%data.shape[1]
        df['Arrivé(e) en tête'][i] = col

    if alliances:
        listeCandidats = ['Nathalie ARTHAUD', 'Emmanuel MACRON', 'Jean LASSALLE', 'Éric ZEMMOUR',
                          'Valérie PÉCRESSE', 'Philippe POUTOU', 'NUPES', 'Ext_Droite']
    else :
        listeCandidats = ['Nathalie ARTHAUD', 'Fabien ROUSSEL', 'Emmanuel MACRON', 'Jean LASSALLE',
                          'Marine LE PEN', 'Éric ZEMMOUR', 'Jean-Luc MÉLENCHON', 'Anne HIDALGO',
                          'Yannick JADOT', 'Valérie PÉCRESSE', 'Philippe POUTOU', 'Nicolas DUPONT-AIGNAN']
    for i in range(len(listeCandidats)):
        df['Arrivé(e) en tête'] = df['Arrivé(e) en tête'].apply(lambda x: listeCandidats[i] if x==i else x)

    return df


def sieges(df, alliances=False):
    df0 = arrives_en_tete(df, alliances)
    df_Sieges = pd.DataFrame()
    for col in df0['Arrivé(e) en tête'].unique():
        df_Sieges[col] = df0[df0['Arrivé(e) en tête'] == col].count()
    df_Sieges.reset_index(drop=True, inplace=True)
    df_Sieges = df_Sieges.iloc[0, :]
    return df_Sieges


def selectionnes(df, alliances=False):
    df = preprocess(df)

    if alliances:
        df['NUPES'] = (df['Fabien ROUSSEL'] + df['Jean-Luc MÉLENCHON']
                       + df['Yannick JADOT'] + df['Anne HIDALGO'])
        df['Ext_Droite'] = (df['Marine LE PEN'] + df['Nicolas DUPONT-AIGNAN'])
        df = df.rename(columns={'Emmanuel MACRON': 'LREM'})
        df.drop(['Fabien ROUSSEL', 'Jean-Luc MÉLENCHON', 'Yannick JADOT', 'Anne HIDALGO',
                 'Marine LE PEN', 'Nicolas DUPONT-AIGNAN'], axis=1, inplace=True)

    for i in range(7, df.shape[1]):
        col = df.columns[i]
        df[col + ' (% des Inscrits)'] = (df[col] * 100 / df['Inscrits'])
        df[col] = (df[col] * 100 / df['Exprimés'])

    df.drop(['Code de la circonscription', 'Inscrits', 'Abstentions',
                  'Votants', 'Blancs', 'Nuls', 'Exprimés'], axis=1, inplace=True)

    stop = alliances * 8 + (1-alliances) * 12
    df['Sélectionnés'] = pd.Series()
    selectionnes = []
    for index in range(df.shape[0]):
        selec = []
        for col in df.columns[:stop]:
            if df[col][index] > 50:
                if df[col + ' (% des Inscrits)'][index] > 25:
                    selec.append(col)
        if selec == []:
            for col in df.columns[stop:2*stop]:
                if df[col][index] >= 12.5:
                    selec.append(col[:-17])
            if len(selec) < 2:
                selec = []
                df_ = df.copy()
                data = df_.values
                amax = data[index, :stop].argmax()
                col = amax%data.shape[1]
                selec.append(df_.columns[col])
                df_.drop(df_.columns[col], axis=1, inplace=True)
                data = df_.values
                amax = data[index, :stop].argmax()
                col = amax%data.shape[1]
                selec.append(df_.columns[col])
        selec.sort()
        selectionnes.append(selec)
    df['Sélectionnés'] = pd.Series(selectionnes, index=df.index)
    df['Gagnant(e)'] = pd.Series('')

    liste2ndTour = []
    for i in range(df.shape[0]):
        cand = df['Sélectionnés'][i]
        if cand not in liste2ndTour:
            liste2ndTour.append(cand)
    print('Les seconds tours : ')
    listeselec = []
    for tour in liste2ndTour:
        print(tour)
        for cand in tour:
            if cand not in listeselec:
                listeselec.append(cand)
    return df