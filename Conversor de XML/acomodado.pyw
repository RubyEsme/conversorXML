from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, PageTemplate, Frame, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Spacer
from reportlab.pdfgen import canvas
from PIL import Image
import os
import qrcode 
from io import BytesIO
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from tkinter import Tk, filedialog, Label, Button, RIGHT
from datetime import datetime, date
from tkinter import messagebox
 

 
class PDFGeneratorApp: 
    def __init__(self, master):
        self.master=master
        master.title("XML TO PDF CONVERTER")

        font_styleE = ("Helvetica", 12)
        self.select_file_button = Button(master, text="SELECCIONAR ARCHIVO", command=self.seleccionar_archivo, font=font_styleE,width=30, height=3, bg="red", fg="white")
        self.select_file_button.pack(side="left")

        self.select_folder_button = Button(master, text="SELECCIONAR RUTA DESTINO", command=self.seleccionar_carpeta_destino, font=font_styleE,width=30, height=3, bg="orange", fg="white")
        self.select_folder_button.pack(side="right")

     # Initialize self.carpeta_destino to a default value
        self.default_route() 

    def default_route(self):
        default_download_folder= os.path.join(os.path.expanduser("~"), "Downloads")
        self.carpeta_destino = default_download_folder    

    def seleccionar_archivo(self):
         try:
            archivo_xml = filedialog.askopenfilename(
                  title="Seleccionar archivo XML",
                  filetypes=[("Archivos XML", "*.xml")]
                 )
            if archivo_xml:
                self.convertir_xml_a_pdf(archivo_xml)
                messagebox.showinfo("EXITO!", f"Archivo PDF generado en {os.path.join(self.carpeta_destino, os.path.basename(archivo_xml).replace('.xml', '.pdf'))}")
            else: 
                messagebox.showinfo("Error", f"No archivo Seleccionado")    
         except (FileNotFoundError, PermissionError) as e:
                messagebox.showinfo("Aviso", f"Cierre PDF() para continuar. {str(e)}")
    

    def seleccionar_carpeta_destino(self):
        folder_selected = filedialog.askdirectory(title="Seleccionar Carpeta De Destino")

        if folder_selected:
            self.carpeta_destino = folder_selected
        else:
            messagebox.showinfo("No Ruta Elegida", "SE DESCARGARA EN DOWNLOADS")
            self.default_route()



    def convertir_xml_a_pdf(self,archivo_xml):
        # Generar un nombre de archivo PDF a partir del nombre del archivo XML
        nombre_pdf = os.path.basename(archivo_xml).replace(".xml", ".pdf")
        archivo_pdf = os.path.join(self.carpeta_destino, nombre_pdf)

        # Crear la carpeta de destino si no existe
        os.makedirs(self.carpeta_destino, exist_ok=True)

        # Eliminar el archivo PDF si ya existe
        if os.path.exists(archivo_pdf):
            os.remove(archivo_pdf)

        

        # Parsear el archivo XML
        tree = ET.parse(archivo_xml)
        root = tree.getroot()

       # Crear un lienzo para el archivo PDF
        c = canvas.Canvas(archivo_pdf, pagesize=letter)

        # Draw rectangles around different sections
        self.draw_rectangle(c, 8, 550, 280, 220, "D1CCCB")  # Rectangle around comprobante information left
        self.draw_rectangle(c, 315, 690, 280, 75, "D1CCCB")# Rectangle around Emisor information right
        self.draw_rectangle(c, 315, 580, 280, 95, "D1CCCB")# Rectangle around receptor information right
        self.draw_rectangle(c, 8, 70, 590, 470, "D1CCCB")# Rectangle around conceptos information left
        

        # Estilo para el título del cuadro del comprobante
        titulo_style = c.beginText(10, 750)
        titulo_style.setFont("Helvetica-Bold", 16)
        titulo_style.setTextOrigin(10, 750)
        titulo_style.setFillColor(colors.black)  # Establecer el color del texto a negro
        titulo_style.textLine("Información del Comprobante")
        c.drawText(titulo_style)

        # Estilo para el contenido del cuadro del comprobante
        contenido_style = c.beginText(10, 735)
        contenido_style.setFillColor(colors.black)  # Establecer el color del texto a negro
        contenido_style.setFont("Helvetica", 12)

        # Agregar información del comprobante al PDF
        contenido_style.textLine(f"Versión: {root.get('Version')}")
        contenido_style.textLine(f"Serie: {root.get('Serie')}")
        contenido_style.textLine(f"Folio: {root.get('Folio')}")
        contenido_style.textLine(f"Fecha: {root.get('Fecha')}")
        contenido_style.textLine(f"Forma de Pago: {root.get('FormaPago')}")
        contenido_style.textLine(f"No. de Certificado: {root.get('NoCertificado')}")
        contenido_style.textLine(f"Subtotal: {root.get('SubTotal')}")
        contenido_style.textLine(f"Moneda: {root.get('Moneda')}")
        contenido_style.textLine(f"Total: {root.get('Total')}")
        contenido_style.textLine(f"Tipo de Comprobante: {root.get('TipoDeComprobante')}")
        contenido_style.textLine(f"Método de Pago: {root.get('MetodoPago')}")
        contenido_style.textLine(f"Lugar de Expedición: {root.get('LugarExpedicion')}")
        contenido_style.textLine(f"Exportación: {root.get('Exportacion')}")
        
        c.drawText(contenido_style)

        # Acceder al nodo del emisor
        emisor_node = root.find(".//{http://www.sat.gob.mx/cfd/4}Emisor")

        # Obtener los atributos del nodo del emisor
        nombre_emisor = emisor_node.get("Nombre")
        regimen_fiscal = emisor_node.get("RegimenFiscal")
        rfc_emisor = emisor_node.get("Rfc")

        # Estilo para el título del cuadro del emisor
        titulo_emisor_style = c.beginText(320, 750)
        titulo_emisor_style.setFont("Helvetica-Bold", 16)
        titulo_emisor_style.setTextOrigin(320, 750)

        c.setFillColorRGB(0,0,0) #fondo negro 
        titulo_emisor_style.textLine("Información del Emisor")
        c.drawText(titulo_emisor_style)

        # Estilo para el contenido del cuadro del emisor
        contenido_emisor_style = c.beginText(320, 735)
        contenido_emisor_style.setFont("Helvetica", 10)

        # Agregar información del emisor al PDF
        contenido_emisor_style.textLine(f"Nombre del Emisor: {nombre_emisor}")
        contenido_emisor_style.textLine(f"Regimen Fiscal: {regimen_fiscal}")
        contenido_emisor_style.textLine(f"RFC del Emisor: {rfc_emisor}")
        
        c.drawText(contenido_emisor_style)

        #Receptor
            
        receptor_node = root.find(".//{http://www.sat.gob.mx/cfd/4}Receptor")

        # Obtener los atributos del nodo del receptor
        nombre_receptor = receptor_node.get("Nombre")
        domicilio_fiscalReceptor = receptor_node.get("DomicilioFiscalReceptor")
        regimen_fiscalReceptor = receptor_node.get("RegimenFiscalReceptor")
        rfc_receptor = receptor_node.get("Rfc")
        usoCFDI = receptor_node.get("UsoCFDI")

        # Estilo para el título del cuadro del receptor
        titulo_receptor_style = c.beginText(320, 660)
        titulo_receptor_style.setFont("Helvetica-Bold", 16)
        titulo_receptor_style.setTextOrigin(320, 660)
        titulo_receptor_style.textLine("Información del Receptor")
        c.drawText(titulo_receptor_style)

        # Estilo para el contenido del cuadro del receptor
        contenido_receptor_style = c.beginText(320, 645)
        contenido_receptor_style.setFont("Helvetica", 12)

        # Agregar información del receptor al PDF
        contenido_receptor_style.textLine(f"Nombre : {nombre_receptor}")
        contenido_receptor_style.textLine(f"Domicilio Fiscal: {domicilio_fiscalReceptor}")
        contenido_receptor_style.textLine(f"Regimen Fiscal: {regimen_fiscalReceptor}")
        contenido_receptor_style.textLine(f"RFC: {rfc_receptor}")
        contenido_receptor_style.textLine(f"Uso de CFDI : {usoCFDI}")
        
        c.drawText(contenido_receptor_style)

        #conceptos
            
        conceptos_node = root.find(".//{http://www.sat.gob.mx/cfd/4}Concepto")

        # Obtener los atributos del nodo de conceptos
        cantidad_conceptos = conceptos_node.get("Cantidad")
        claveProdServ_conceptos = conceptos_node.get("ClaveProdServ")
        claveUnidad_conceptos = conceptos_node.get("ClaveUnidad") 
        desc_conceptos= conceptos_node.get("Descripcion")
        objImp_conceptos= conceptos_node.get("ObjetoImp")
        importe_conceptos = conceptos_node.get("Importe")
        valorUni_conceptos = conceptos_node.get("ValorUnitario")

        
        # Estilo para el título del cuadro del conceptos
        titulo_conceptos_style = c.beginText(10, 523)
        titulo_conceptos_style.setFont("Helvetica-Bold", 16)
        titulo_conceptos_style.setTextOrigin(10, 523)
        titulo_conceptos_style.textLine("Información de Conceptos")
        c.drawText(titulo_conceptos_style)

        # Estilo para el contenido del cuadro del conceptos
        contenido_conceptos_style = c.beginText(10, 500)
        contenido_conceptos_style.setFont("Helvetica", 13)
        contenido_conceptos2 = c.beginText(300, 500)
        contenido_conceptos2.setFont("Helvetica", 13)
        conteDesc_style= c.beginText(10, 445)
        conteDesc_style.setFont("Helvetica", 13)

        # Agregar información del receptor al PDF
        contenido_conceptos_style.textLine(f"Cantidad : {cantidad_conceptos}")
        contenido_conceptos_style.textLine(f"Clave Prod Serv : {claveProdServ_conceptos}")
        contenido_conceptos2.textLine(f"Clave Unidad : {claveUnidad_conceptos}")
        contenido_conceptos_style.textLine(f"Valor Unitario : {valorUni_conceptos}")
        contenido_conceptos2.textLine(f"ObjetoImp: {objImp_conceptos}")
        contenido_conceptos2.textLine(f"Importe: {importe_conceptos}")
        conteDesc_style.textLine(f"Descripcion: {desc_conceptos}")
        
        c.drawText(contenido_conceptos_style)
        c.drawText(contenido_conceptos2)
        c.drawText(conteDesc_style)

        #Impuestos y Traslados
            
        imp_node = root.find(".//{http://www.sat.gob.mx/cfd/4}Traslado")
        impuesto_nodes = root.findall(".//{http://www.sat.gob.mx/cfd/4}Impuestos") #findalll porque en el xml tiene mas nodos similares
        # Obtener los atributos del nodo de traslados e impuestos
        base = imp_node.get("Base")
        impuesto = imp_node.get("Impuesto")
        importe = imp_node.get("Importe") 
        cuota= imp_node.get("TasaOCuota")
        tipoFactor= imp_node.get("TipoFactor")
        impuesto_node = impuesto_nodes[1] #para acceder a el segundo nodo
        totalImpTras= impuesto_node.get("TotalImpuestosTrasladados")
        
        # Estilo para el título del cuadro del impuestos
        titulo_imp_style = c.beginText(10, 400)
        titulo_imp_style.setFont("Helvetica-Bold", 16)
        titulo_imp_style.setTextOrigin(10, 400)
        titulo_imp_style.textLine("Información de Impuestos Y Traslados")
        c.drawText(titulo_imp_style)

        # Estilo para el contenido del cuadro de impuestos
        contenido_imp_style = c.beginText(10, 380)
        contenido_imp_style.setFont("Helvetica", 12)
      

        # Agregar información  al PDF
        contenido_imp_style.textLine(f"Base: {base}")
        contenido_imp_style.textLine(f"Impuesto : {impuesto}")
        contenido_imp_style.textLine(f"Importe : {importe}")
        contenido_imp_style.textLine(f"Tasa o Cuota : {cuota}")
        contenido_imp_style.textLine(f"Tipo Factor : {tipoFactor}")
        contenido_imp_style.textLine(f"Total Impuestos Trasladados : {totalImpTras}")
        c.drawText(contenido_imp_style)

        #COMPLEMENTOS
        def agregar_lineas_con_salto(texto, longitud_maxima):
    
            # Divide el texto en líneas de longitud máxima
            lineas = []

            while len(texto) > longitud_maxima:
                # Corta el texto para que tenga una longitud máxima y agrega la parte cortada a la lista de líneas
                linea_actual = texto[:longitud_maxima]
                lineas.append(linea_actual)

                # Actualiza el texto para excluir la parte que ya ha sido agregada
                texto = texto[longitud_maxima:]

            # Agrega la última parte del texto que puede ser menor que la longitud máxima
            lineas.append(texto)

            return lineas


            
        complementos_node = root.find(".//{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital") #ruta que sigue para buscar lo indicado

        # Obtener los atributos del nodo de complementos
        selloCFD = complementos_node.get("SelloCFD")
        noCertSAT = complementos_node.get("NoCertificadoSAT")
        UUID = complementos_node.get("UUID")
        fechaTimbrado = complementos_node.get("FechaTimbrado")
        selloSat = complementos_node.get("SelloSAT")
        

        # Estilo para el contenido del cuadro del complementos
        contenido_comp_style = c.beginText(10, 270)
        contenido_comp_style.setFont("Helvetica", 8)
        UUID_content = c.beginText(70, 150)
        UUID_content.setFont("Helvetica", 10)
        uuidTitle = c.beginText(10, 150)
        uuidTitle.setFont("Helvetica-Bold", 12)
        uuidTitle.textLine("UUID:")

        # Agregar información de complementos al PDF con saltos de línea
        selloCFD_lineas = agregar_lineas_con_salto(f"SelloCFD : {selloCFD}", 90)
        selloCFD_lineas = agregar_lineas_con_salto(f"SelloCFD : {selloCFD}", 80)
        noCertSAT_lineas = agregar_lineas_con_salto(f"Numero Certificado SAT: {noCertSAT}", 80)
        UUID_lineas = agregar_lineas_con_salto(f"{UUID}", 80)
        fechaTimbrado_lineas = agregar_lineas_con_salto(f"Fecha Timbrado: {fechaTimbrado}", 80)
        selloSat_lineas = agregar_lineas_con_salto(f"Sello SAT: {selloSat}", 80)

        # Agrega las líneas al contenido del PDF
        for linea in selloCFD_lineas:
            contenido_comp_style.textLine(linea)

        for linea in noCertSAT_lineas:
            contenido_comp_style.textLine(linea)

        for linea in UUID_lineas:
            UUID_content.textLine(linea)

        for linea in fechaTimbrado_lineas:
            contenido_comp_style.textLine(linea)

        for linea in selloSat_lineas:
            contenido_comp_style.textLine(linea)

        c.drawText(contenido_comp_style)
        c.drawText(uuidTitle)
        c.drawText(UUID_content)

        def generate_qr_code(data):
            qr = qrcode.QRCode(
                version=5,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=5,
                border=2,
                )
            qr.add_data(data)
            qr.make(fit=True)

            img= qr.make_image(fill_color="black", back_color="white")
            img_byte_array = BytesIO()
            img.save(img_byte_array, format="PNG")
            img_byte_array.seek(0)

            return img_byte_array

        def add_qr_to_pdf(qr_image, canvas, title_text, qr_code_coords):
            #adding title text
            title_style = canvas.beginText(480,220)
            title_style.setFont("Helvetica-Bold", 16)
            title_style.textLine(title_text)
            canvas.drawText(title_style)

            #adding qr code

            image_data =Image.open(qr_image)
            canvas.drawInlineImage(image_data, *qr_code_coords, width=110, height=110)
            
        try:        
            encabezado_node = root.find(".//{https://www.totalplay.com/Schemas/Documentos}Encabezado")

            
            qr_code_url = encabezado_node.get('qrCode')
        

            qr_code_image = generate_qr_code(qr_code_url)
            

            add_qr_to_pdf(qr_code_image,c,"CÓDIGO QR:", (470, 100))
        except Exception as e:
            print("pdf no contiene QRcode")
    
        # Guardar el PDF
        c.showPage()
        c.save()
        
    def draw_rectangle(self, canvas, x, y, width, height, color="#FFA500"):
        canvas.setStrokeColorRGB(*self.hex_to_rgb(color))
        canvas.setFillColorRGB(*self.hex_to_rgb(color))
        canvas.rect(x, y, width, height, fill=1)

    def hex_to_rgb(self, hex_color):
        # Convierte el color hexadecimal a una tupla RGB
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
   

def main():
    root = Tk()
    app = PDFGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
