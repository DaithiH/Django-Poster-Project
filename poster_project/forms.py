from django import forms

class PosterForm(forms.Form):
    # With user defined sizes
    #width = forms.IntegerField(label= 'New Width', min_value= 1)
    #height = forms.IntegerField(label= 'New Height', min_value= 1)
    image = forms.ImageField(label= 'Upload Image')
    dpi_new = forms.IntegerField(label= "DPI", initial= 300)

    # Field to select poster size
    size_choice = forms.ChoiceField(
        choices = [
            ('small', 'Small (420 × 594 mm, 2 sheets wide × 2 sheets high) '),
            ('medium', 'Medium (630 × 891 mm, 3 sheets wide × 3 sheets high)'),
            ('large', 'Large (1050 × 1188 mm), 5 sheets wide × 4 sheets high' )
        ],
        label= 'Poster Size'
    ) 