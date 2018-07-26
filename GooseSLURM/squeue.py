
# ==================================================================================================

def colors(theme='dark'):
  r'''
Return named colors:

*   selection
*   queued

:options:

  **theme** ([``'dark'``] | ``<str>``)
    Select color-theme.
  '''

  if theme == 'dark':
    return \
      {
        'selection' : '1;32;40',
        'queued'    : '0;37',
      }

  return \
  {
  'selection' : '',
  'queued'    : '',
  }

# ==================================================================================================
