
import webbrowser
from Analizador import AnalizadorLexico
import PySimpleGUI as sg 
from tkinter import font as tkfont
import sys

application_active = False 


class RedirectText:
    def __init__(self, window):
        ''' constructor '''
        self.window = window
        self.saveout = sys.stdout

    def write(self, string):
        self.window['_OUT_'].Widget.insert("end", string)

    def flush(self):
        sys.stdout = self.saveout 
        sys.stdout.flush()

##-----CONFIGURACION INICIAL-----------------------##

save_user_settings = False

if save_user_settings:
    import shelve
    settings = shelve.open('app_settings')
else:
    settings = {}

if len(settings.keys()) == 0:
    settings['theme'] = 'BluePurple'
    settings['themes'] = sg.list_of_look_and_feel_values()
    settings['font'] = ('Consolas', 12)
    settings['tabsize'] = 4
    settings['filename'] = None
    settings['body'] = ''
    settings['info'] = '> New File <'
    settings['out'] = ''


sg.change_look_and_feel(settings['theme'])

outstring = "CONFIGURACION INICIAL\n"+"-"*40+"\nTema"+"."*10+" {}\nTamaño de fuenta"+"."*7+" {}\nFuente"+"."*11+" {} {}\nArchivo abierto"+"."*6+" {}\n\n"
settings.update(out = outstring.format(settings['theme'], settings['tabsize'], settings['font'][0], settings['font'][1], settings['filename']))

def close_settings():
    settings.update(filename=None, body='', out='', info='> New File <')
    if save_user_settings:
        settings.close()


##----CONFIGURACION DE LA PANTALLA-----------------------------------##

def main_window(settings):
    elem_width= 80 
    menu_layout = [
        ['Archivo',['Nuevo','Abrir','Guardar','Guardar Como','---','Salir']],
        ['Apariencia',['Temas', settings['themes'],'Fuente','Tamaño de letras','Mostrar configuración']],
        ['Analizar',['Analizar']],
        ['Reportes',['Reporte de Tokens','Reporte de Errores','Reporte de Usuario','Reporte Tecnico']]]

    col1 = sg.Column([[sg.Multiline(default_text=settings['body'], font=settings['font'], key='_BODY_', size=(elem_width,20))]])
    col2 = sg.Column([[sg.Multiline(default_text=settings['out'], font=settings['font'], key='_OUT_', autoscroll=True, size=(elem_width,8))]])         

    window_layout = [
        [sg.Menu(menu_layout)],
        [sg.Text(settings['info'], key='_INFO_', font=('Consolas',11), size=(elem_width,1))],
        [sg.Pane([col1, col2])]]

    window = sg.Window('Analizador Lexico', window_layout, resizable=True, margins=(0,0), return_keyboard_events=True)
    return window


##----ARCHIVOS--------------------------------##

def new_file(window): # CTRL+N 
    window['_BODY_'].update(value='')
    window['_INFO_'].update(value='> New File <')
    settings.update(filename=None, body='', info='> New File <')

def open_file(window): # CTRL+O 
    try: 
        filename = sg.popup_get_file('File Name:', title='Open', no_window=True)
    except:
        return
    if filename not in (None,''):
        with open(filename,'r') as f:
            file_text = f.read()
        window['_BODY_'].update(value=file_text)
        window['_INFO_'].update(value=filename.replace('/',' > '))
        settings.update(filename=filename, body=file_text, info=filename.replace('/',' > '))

def save_file(window, values): # CTRL+S 
    filename = settings.get('filename')
    if filename not in (None,''):
        with open(filename,'w') as f:
            f.write(values['_BODY_'])
        window['_INFO_'](value=filename.replace('/',' > '))
        settings.update(filename=filename, info=filename.replace('/',' > '))
    else:
        save_file_as(window, values)

def save_file_as(window, values):
    try: 
        filename = sg.popup_get_file('Save File', save_as=True, no_window=True)
    except:
        return
    if filename not in (None,''):
        with open(filename,'w') as f:
            f.write(values['_BODY_'])
        window['_INFO_'](value=filename.replace('/',' > '))
        settings.update(filename=filename, info=filename.replace('/',' > '))


##----REPORTES------------------------------##
def show_ReporteUsuario():
    webbrowser.open('Manual de usuario.pdf')

def show_ReporteTecnico():
    webbrowser.open('Manual tecnico.pdf')


##----APARIENCIA------------------------------##

def change_theme(window, event, values):

    settings.update(theme=event, body=values['_BODY_'], out=values['_OUT_'])
    sg.change_look_and_feel(event)
    window.close()

def change_font(window):

    font_name, font_size = settings.get('font')
    font_list = sorted([f for f in tkfont.families() if f[0]!='@'])
    if not font_name in font_list:
      font_name = font_list[0]
    font_sizes = [8,9,10,11,12,14]
    font_layout = [
        [sg.Combo(font_list, key='_FONT_', default_value=font_name), 
         sg.Combo(font_sizes, key='_SIZE_', default_value=font_size)],[sg.OK(), sg.Cancel()]]
    font_window = sg.Window('Font', font_layout, keep_on_top=True)
    font_event, font_values = font_window.read()
    if font_event not in (None,'Exit'):
        font_selection = (font_values['_FONT_'], font_values['_SIZE_'])
        if font_selection != settings['font']:
            settings.update(font=font_selection)
            window['_BODY_'].update(font=font_selection)
            window['_OUT_'].update(font=font_selection)
            print(f"Font........... {(font_name, font_size)} => {font_selection}\n")
    font_window.close()

def change_tabsize(window):
    tab_layout = [[sg.Slider(range=(1,8), default_value=settings['tabsize'], orientation='horizontal', key='_SIZE_'), sg.OK(size=(5,2))]]
    tab_window = sg.Window('Tab Size', tab_layout, keep_on_top=True)
    tab_event, tab_values = tab_window.read()
    if tab_event not in (None, 'Exit'):
        old_tab_size = settings['tabsize']
        new_tab_size = int(tab_values['_SIZE_'])
        if new_tab_size != old_tab_size:
            settings.update(tabsize=new_tab_size)
            set_tabsize(window, new_tab_size)
            print(f"Tab size....... {old_tab_size} => {new_tab_size}\n")
    tab_window.close()

def set_tabsize(window, size=4): 
    font = tkfont.Font(font=settings.get('font'))
    tab_width = font.measure(' '*size)
    window['_BODY_'].Widget.configure(tabs=(tab_width,)) 
    settings.update(tabsize=size) 

def show_settings():
    print(f"Theme.......... {settings['theme']}")
    print(f"Tab size....... {settings['tabsize']}")
    print( "Font.............. {}, {}".format(*settings['font']))
    print(f"Open file...... {settings['filename']}\n")


##----ANALIZAR---------------------------------##

def run_module(): # F5 
        countLabel = []
        cadena = open(settings.get('filename'),'r+').read()

        lexico = AnalizadorLexico()

        lexico.analizar(cadena)

        listaTokens = lexico.listaTokens

        strHtml = ''
        strInfo = '<div id="div1" style="visibility: hidden;">'
        strSrciptInfoOption = ''
        strSrciptInfo = ''
        strHtmlinicio ='''<!DOCTYPE html>
                    <html>
                        <head><title>Formulario</title></head>
                        <body>
                            <form>
                                '''
        f = open('Formulario.html','w')
        for i in range(0,len(listaTokens)):
            #Llenado de etiquetas
            if listaTokens[i].tipo == 'dosPuntos' and listaTokens[i+1].lexema == 'etiqueta' and listaTokens[i-1].tipo == 'reservada_tipo' and listaTokens[i+2].tipo == 'coma':
                for j in range(i,len(listaTokens)):
                    if listaTokens[j].tipo == 'mayorque' and listaTokens[j+1].tipo == 'coma':
                        break
                    if listaTokens[j].tipo == 'dosPuntos' and listaTokens[j+1].tipo == 'texto' and listaTokens[j-1].tipo == 'reservada_valor':
                        strHtml += '<label for="{}">{}</label><br>\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                        strInfo += '<label for="{}1" >{}</label><br>\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                        strSrciptInfo += 'document.getElementById("{}1").value = document.getElementById("{}").value;\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                        
                        
                        countLabel.append(listaTokens[j+1].lexema)
                        break
            #Llenado de textos
            if listaTokens[i].tipo == 'dosPuntos' and listaTokens[i+1].lexema == 'texto' and listaTokens[i-1].tipo == 'reservada_tipo' and listaTokens[i+2].tipo == 'coma':
                for j in range(i,len(listaTokens)):
                    if listaTokens[j].tipo == 'mayorque' and listaTokens[j+1].tipo == 'coma':
                        break
                    if listaTokens[j].tipo == 'dosPuntos' and listaTokens[j+1].tipo == 'texto' and listaTokens[j-1].tipo == 'reservada_valor':
                        for k in range(j,len(listaTokens)):
                            if listaTokens[k].tipo == 'mayorque' and listaTokens[k+1].tipo == 'coma':
                                strHtml += '<input type="text" id="{}" name="{}"><br>\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                                strInfo += '<input type="text" id="{}1" name="{}"  ><br>\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                                strSrciptInfo += 'document.getElementById("{}1").value = document.getElementById("{}").value;\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                                
                                
                                break
                            if listaTokens[k].tipo == 'dosPuntos' and listaTokens[k+1].tipo == 'texto' and listaTokens[k-1].tipo == 'reservada_fondo':
                                strHtml += '<input type="text" id="{}" name="{}" placeholder="{}"><br>\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema,listaTokens[k+1].lexema)
                                strInfo += '<input type="text" id="{}1" name="{}"  ><br>\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                                strSrciptInfo += 'document.getElementById("{}1").value = document.getElementById("{}").value;\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                                
                                
                                break
            #Llenado de group-radio
            if listaTokens[i].tipo == 'dosPuntos' and listaTokens[i+1].lexema == 'grupo-radio' and listaTokens[i-1].tipo == 'reservada_tipo' and listaTokens[i+2].tipo == 'coma':
                for j in range(i,len(listaTokens)):
                    if listaTokens[j].tipo == 'mayorque' and listaTokens[j+1].tipo == 'coma':
                        break
                    if listaTokens[j].tipo == 'dosPuntos' and listaTokens[j+1].tipo == 'texto' and listaTokens[j-1].tipo == 'reservada_nombre':
                        strHtml += '<label for="{}">{}</label>\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                        strInfo += '<label for="{}"  >{}</label>\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                        strInfo += '<input type="text" id="{}1"  ><br>\n'.format(listaTokens[j+1].lexema)
                        strSrciptInfo += 'var {} = document.getElementsByName("{}");\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                        strSrciptInfo += 'for(i=0; i<'+listaTokens[j+1].lexema+'.length; i++){\n'
                        strSrciptInfo += 'if('+listaTokens[j+1].lexema+'[i].checked){\n'
                        strSrciptInfo += 'document.getElementById("{}1").value = {}[i].value;\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                        strSrciptInfo += "} }\n"
                        
                        
                        for k in range(j,len(listaTokens)):
                            if listaTokens[k].tipo == 'mayorque' and listaTokens[k+1].tipo == 'coma':
                                break
                            if listaTokens[k].tipo == 'dosPuntos' and listaTokens[k+1].tipo == 'corcheteIzquierdo' and listaTokens[k-1].tipo == 'reservada_valores':
                                for l in range(k,len(listaTokens)):
                                    if listaTokens[l].tipo == 'corcheteDerecho':
                                        strHtml += '<input type="radio" id="{}" name="{}" value="{}">\n'.format(listaTokens[l-1].lexema,listaTokens[j+1].lexema,listaTokens[l-1].lexema)
                                        strHtml += '<label for="{}">{}</label><br>\n'.format(listaTokens[l-1].lexema,listaTokens[l-1].lexema)
                                        break
                                    if listaTokens[l].tipo == 'coma' and listaTokens[l-1].tipo == 'texto' and listaTokens[l+1].tipo == 'texto':
                                        strHtml += '<input type="radio" id="{}" name="{}" value="{}">\n'.format(listaTokens[l-1].lexema,listaTokens[j+1].lexema,listaTokens[l-1].lexema)
                                        strHtml += '<label for="{}">{}</label>\n'.format(listaTokens[l-1].lexema,listaTokens[l-1].lexema)
            #Llenado de group-option
            if listaTokens[i].tipo == 'dosPuntos' and listaTokens[i+1].lexema == 'grupo-option' and listaTokens[i-1].tipo == 'reservada_tipo' and listaTokens[i+2].tipo == 'coma':
                for j in range(i,len(listaTokens)):
                    if listaTokens[j].tipo == 'mayorque'  and listaTokens[j+1].tipo == 'coma':
                        break
                    if listaTokens[j].tipo == 'dosPuntos' and listaTokens[j+1].tipo == 'texto' and listaTokens[j-1].tipo == 'reservada_nombre':
                        strHtml += '<label for="{}">{}</label>\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                        strInfo += '<label for="{}"  >{}</label>\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                        strInfo += '<input type="text" id="{}1"  ><br>\n'.format(listaTokens[j+1].lexema)
                        strSrciptInfoOption += 'var {} = document.getElementById("{}");\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema)
                        strSrciptInfoOption += 'document.getElementById("{}1").value = {}.options[{}.selectedIndex].value;\n'.format(listaTokens[j+1].lexema,listaTokens[j+1].lexema,listaTokens[j+1].lexema)

                        for k in range(j,len(listaTokens)):
                            if listaTokens[k].tipo == 'mayorque':
                                break
                            if listaTokens[k].tipo == 'dosPuntos' and listaTokens[k+1].tipo == 'corcheteIzquierdo' and listaTokens[k-1].tipo == 'reservada_valores':
                                strHtml += '<select id="{}">'.format(listaTokens[j+1].lexema)
                                for l in range(k,len(listaTokens)):
                                    if listaTokens[l].tipo == 'corcheteDerecho':
                                        strHtml += '<option value="{}">{}</option>\n'.format(listaTokens[l-1].lexema,listaTokens[l-1].lexema)
                                        strHtml += '</select><br>\n'
                                        break
                                    if listaTokens[l].tipo == 'coma' and listaTokens[l-1].tipo == 'texto' and listaTokens[l+1].tipo == 'texto':
                                        strHtml += '<option value="{}">{}</option>\n'.format(listaTokens[l-1].lexema,listaTokens[l-1].lexema)
            #Llenado de botones
            if listaTokens[i].tipo == 'dosPuntos' and listaTokens[i+1].lexema == 'boton' and listaTokens[i-1].tipo == 'reservada_tipo' and listaTokens[i+2].tipo == 'coma':
                for j in range(i,len(listaTokens)):
                    if listaTokens[j].tipo == 'mayorque' and listaTokens[j+1].tipo == 'coma':
                        break
                    if listaTokens[j].tipo == 'dosPuntos' and listaTokens[j+1].tipo == 'texto' and listaTokens[j-1].tipo == 'reservada_valor':
                        for k in range(j,len(listaTokens)):
                            if listaTokens[k].tipo == 'mayorque' and listaTokens[k+1].tipo == 'coma':
                                break
                            if listaTokens[k].tipo == 'dosPuntos' and listaTokens[k+1].tipo == 'texto' and listaTokens[k-1].tipo == 'reservada_evento':
                                if listaTokens[k+1].lexema == 'entrada':
                                    EntrastaHTML = open('Entrada.html','w')
                                    strEntradHtml = ''
                                    strEntrada = ''
                                    Archivo = open(settings.get('filename'),'r')
                                    strEntradHtml = '''<!DOCTYPE html>
                    <html>
                        <head><title>Formulario</title></head>
                        <body>
                            
                                '''
                                    for linea in Archivo:
                                        strEntrada += linea +'<br>'
                                    strHtml += ' <input type="button" onclick="myFunction()" value="{}"> <br>'.format(listaTokens[j+1].lexema)
                                    strHtml += '<iframe id="entrada" src = "Entrada.html" style="visibility: hidden;"></iframe>'.format(strEntrada)
                                    strHtml += '''<script> 
                                                function myFunction() {
                                                document.getElementById("entrada").style.visibility = "visible";
                                                }
                                                </script>'''
                                    strEntradHtml += '<p >{}</p>'.format(strEntrada)
                                    strEntradHtml += '''   
                        </body>
                    </html>'''
                                    EntrastaHTML.write(strEntradHtml)
                                    EntrastaHTML.close()
                                if listaTokens[k+1].lexema == 'info':
                                    strSrciptInfo += 'document.getElementById("div1").style.visibility = "visible";\n'
                                    strHtml += ' <input type="button" onclick="myFunction1()" value="{}"> <br>'.format(listaTokens[j+1].lexema)
                                    strHtml += '''<script> 
                                                function myFunction1() {'''
                                    strHtml += strSrciptInfoOption+ strSrciptInfo+'}'
                                    strHtml +=  '''</script>'''
                                    strHtml += strInfo + '</div>'
                                break
                    
        strHtml += '''        </form>
                        </body>
                    </html>'''
        f.write(strHtmlinicio+strHtml)
        f.close()
        webbrowser.open('Formulario.html') 

def obtenerValor(token,diccionario):
    if token.tipo == 'numero':
        return int(token.lexema)
    elif token.tipo == 'identificador':
        return diccionario[token.lexema]



##----MAIN------------------------------------##

window = main_window(settings)
redir = RedirectText(window)
sys.stdout = redir

while True:
    event, values = window.read(timeout=1)

    if not application_active:
        application_active = True
        set_tabsize(window)

    if event in (None, 'Salir'):
        close_settings()
        break
    if event in ('Nuevo','n:78'):
        new_file(window)
    if event in ('Abrir','o:79'):
        open_file(window)
    if event in ('Guardar','s:83'):
        save_file(window, values)
    if event in ('Guardar Como',):
        save_file_as(window, values)
    if event in ('Fuente',):
        change_font(window)
    if event in ('Tamaño de letras',):
        change_tabsize(window)
    if event in ('Mostrar configuración',):
        show_settings()
    if event in ('Analizar', 'F5:116' ):
        run_module()
    if event in settings['themes']: 

        application_active = False
        change_theme(window, event, values)
        sys.stdout = redir.saveout
        window = main_window(settings)
        redir = RedirectText(window)
        sys.stdout = redir
    if event in ('Reporte Tecnico',):
        show_ReporteTecnico()
    if event in ('Reporte de Tokens',):
        cadena = open(settings.get('filename'),'r+').read()
        lexico = AnalizadorLexico()
        lexico.analizar(cadena)
        lexico.imprimirTokens()
    if event in ('Reporte de Errores',):
        lexico = AnalizadorLexico()
        cadena = open(settings.get('filename'),'r+').read()
        lexico.analizar(cadena)
        lexico.imprimirErrores()
    if event in ('Reporte de Usuario',):
        show_ReporteUsuario()