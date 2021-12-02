from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Datos Personales'), {'fields': ('name',)}),
        (
            _('Permisos'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (('Sucursales'), {'fields': ('sucursales',)}),
        (_('Ultimo Acceso'), {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )

# Agregamos inlines para las Recetas
class IngredienteRecetaInline(admin.TabularInline):
    model = models.IngredienteReceta
    extra = 1

class IngredienteAdmin(admin.ModelAdmin):
    inlines = (IngredienteRecetaInline,)
    search_fields = ['nombre', 'codigo']

class RecetaAdmin(admin.ModelAdmin):
    inlines = (IngredienteRecetaInline,)
    search_fields = ['nombre', 'codigo_pos']

# ===========================================
# ===========================================

@admin.register(models.Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    fields = ('codigo', 'nombre', 'categoria', 'factor_peso')
    list_display = ('nombre', 'codigo')
    ordering = ('nombre',)
    search_fields = ('codigo', 'nombre')
    list_filter = ('categoria',)

@admin.register(models.ProductoSinRegistro)
class ProductoSinRegistroAdmin(admin.ModelAdmin):
    fields = ('codigo_pos', 'nombre', 'sucursal', 'unidades', 'importe', 'caja' 'fecha')
    list_display = ('codigo_pos', 'nombre', 'sucursal', 'unidades', 'importe', 'fecha')
    ordering = ('-fecha',)
    list_filter = ('fecha', 'sucursal')

@admin.register(models.Producto)
class ProductoAdmin(admin.ModelAdmin):
    fields = ('ingrediente', 'nombre_marca', 'capacidad', 'codigo_barras', 'peso_nueva', 'peso_cristal', 'precio_unitario')
    list_display = ('nombre_marca', 'codigo_barras', 'capacidad')
    ordering = ('nombre_marca',)
    search_fields = ('codigo_barras', 'nombre_marca')

@admin.register(models.Botella)
class BotellaAdmin(admin.ModelAdmin):
    fields = (
        'sat_hash',
        'folio',
        'url',
        'producto',
        'nombre_marca',
        'estado',
        'fecha_baja',
        'usuario_alta',
        'sucursal',
        'almacen',
        'peso_nueva',
        'peso_cristal',
        'peso_inicial',
        'peso_actual',
        'precio_unitario'
    )
    list_display = ('nombre_marca', 'sat_hash', 'folio', 'sucursal', 'estado', 'fecha_registro')
    ordering = ('-fecha_registro',)
    list_filter = ('sucursal', 'fecha_registro')
    search_fields = ('sat_hash', 'folio', 'nombre_marca')




admin.site.register(models.Cliente)
admin.site.register(models.Sucursal)
admin.site.register(models.Proveedor)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Categoria)
#admin.site.register(models.Ingrediente)
admin.site.register(models.Receta)
admin.site.register(models.IngredienteReceta)
admin.site.register(models.Almacen)
admin.site.register(models.Caja)
admin.site.register(models.Venta)
admin.site.register(models.ConsumoRecetaVendida)
#admin.site.register(models.Producto)
#admin.site.register(models.Botella)
#admin.site.register(models.ProductoSinRegistro)
admin.site.register(models.Inspeccion)
admin.site.register(models.ReporteMermas)