import pandas as pd

d = pd.read_csv('data/svamitva_survey.csv', keep_default_na=False)
Q = pd.read_csv('data/codebook.csv').set_index('variable').question
d['row'] = d.index + 2
d['dist'] = d.q5.str.split(' - ').str[1].str.strip()
d['vill'] = d.q5.str.split(' - ').str[0].str.strip().replace({'Bardenagar': 'Bhardenagar', 'Bhardengar': 'Bhardenagar'})
N = len(d)

def pct(k, n): return f'{k} ({100*k/n:.1f}%)'
def tab(q, by=None):
    print(f'\n## {q}: {Q[q]}')
    print(pd.crosstab(d[q], d['dist'], margins=True).to_string() if by else d[q].value_counts().to_string())

print('N =', N)
print(d.groupby('dist').agg(n=('row', 'size'), villages=('vill', 'nunique'),
      women=('q3', lambda s: (s == 'Female').sum()), mean_age=('q2', 'mean')).round(1))
print(d.groupby(['dist', 'vill']).size())
print('age', d.q2.describe().round(1).to_dict())
print('farming listed in occupation:', d.q4.str.contains('Farmer|Agriculture').sum())
print('survey window:', d.q0.astype(str).str[:10].min(), d.q0.astype(str).str[:10].max())

for q in ['q6','q8','q9','q12','q14','q15','q17','q19','q21','q22','q23','q24','q25',
          'q26','q27','q28','q30','q31','q32','q34','q35','q36']:
    tab(q, by=True)
print('\nq19 == q20 for all rows:', (d.q19 == d.q20).all())

print('\n## borrowed with 7-12 x bank accepts card')
print(pd.crosstab(d.q31, d.q32, margins=True))
print(pd.crosstab([d.dist, d.q3], d.q31))
print(pd.crosstab(d.q31, d.q35, margins=True))
print(pd.crosstab(d.q21, d.q31, margins=True))

b = d[d.q32 == 'No'].copy()
codes33 = {
  'names_712':  r'7-12|7/12',
  'supporting': r'support|secondary|additional|along with|as well|both the documents|if we want|if required|already submitted|unless it submitted',
  'practice':   r'years|tradition|always|decades|earlier|used to|old procedure|never disbursed|been following|in use|previous|old documents|rather than the latest',
  'risk':       r'risk|chance|issues later|lead to problems|not comfortable|not keen',
  'no_instruction': r'notification',
}
for k, p in codes33.items(): b[k] = b.q33.str.contains(p, case=False, regex=True)
print('\n## Q33 codes, n =', len(b)); print(b[list(codes33)].sum()); print(b.groupby('dist')[list(codes33)].sum())
print('card not collected because bank wants 7-12 (rows 27,29,48):'); print(d[d.row.isin([27,29,48])][['row','dist','q31','q32','q33']].to_string())
print('Sindhudurg: no-mortgage norm stated in Q33:', d[(d.dist=='Sindhudurg') & d.q33.str.contains('mortgag', case=False)].shape[0])

c = d[d.q35 == '8A / 7-12'].copy()
codes38 = {
  'duplicate':  r'already|existing|previous|duplicate|additional|similar|same|another|one more|new one|earlier|original|before|have title|have our|have land|have 8A|have all|olden|old |extra|are good',
  'not_used':   r'not accepted|not in use|nobody|no authority|not work|not needed anywhere|not used|not useful|accepted everywhere|acceptable everywhere|everyone wants|request 7-12|valid and acceptable|serve the purpose|work fine|worked better|works better|good for all|still valid|submitted everywhere',
  'area':       r'discrepanc|different|area',
  'disputes':   r'dispute|neighbo',
}
for k, p in codes38.items(): c[k] = c.q38.str.contains(p, case=False, regex=True)
c.loc[c.row == 2, 'duplicate'] = False
print('\n## Q38 codes, n =', len(c)); print(c[list(codes38)].sum()); print(c.groupby('dist')[list(codes38)].sum())
print('uncoded:', c[~c[list(codes38)].any(axis=1)][['row','q38']].to_string())

gov_rows = [8,15,22,24,25,26,30,33,34,35,42,43,47,50,51,54,55,56]
print('\nQ39 government-not-people:', len(gov_rows), d[d.row.isin(gov_rows)].dist.value_counts().to_dict())

s = d[d.dist == 'Sindhudurg']
print('\nQ37 Sindhudurg: ownership', s.q37.str.contains('ownership|owner', case=False).sum(),
      '| women', s.q37.str.contains('women', case=False).sum(),
      '| accuracy/boundaries/maps', s.q37.str.contains('accura|boundar|map|demarcat', case=False).sum(),
      '| value/develop', s.q37.str.contains('value|develop|price', case=False).sum(),
      '| loan/credit/bank', s.q37.str.contains('loan|credit|bank|mortgag', case=False).sum())

print('\nmedian age by district:', d.groupby('dist').q2.median().to_dict(), '| overall', d.q2.median())
only712 = b.names_712 & ~b[['supporting','practice','risk','no_instruction']].any(axis=1)
print('Q33 answers coded only to names_712:', only712.sum(), 'of', len(b))
print('women never borrowed by district:', d[(d.q3=='Female') & (d.q31=='No')].dist.value_counts().to_dict())
