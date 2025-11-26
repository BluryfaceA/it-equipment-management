import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from utils.api_client import APIClient

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Gestión de Equipos TI",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar cliente API
api = APIClient()

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4788;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# AUTENTICACIÓN
# ============================================

def login_page():
    st.markdown('<h1 class="main-header">🔐 Sistema de Gestión de Equipos TI</h1>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Iniciar Sesión")

        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar", use_container_width=True)

            if submit:
                if username and password:
                    try:
                        response = api.login(username, password)
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state['token'] = data['access_token']
                            st.session_state['user'] = data['user']
                            st.session_state['logged_in'] = True
                            st.rerun()
                        else:
                            st.error("Usuario o contraseña incorrectos")
                    except Exception as e:
                        st.error(f"Error al conectar con el servidor: {str(e)}")
                else:
                    st.warning("Por favor, ingrese usuario y contraseña")

        st.info("👤 Usuario por defecto: **admin** | Contraseña: **admin123**")

# ============================================
# DASHBOARD
# ============================================

def dashboard_page():
    st.markdown('<h1 class="main-header">📊 Dashboard</h1>', unsafe_allow_html=True)

    try:
        response = api.get_dashboard_statistics()
        if response.status_code == 200:
            stats = response.json()

            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Equipos", stats.get('total_equipment', 0))

            with col2:
                upcoming = stats.get('upcoming_maintenance_30_days', 0)
                st.metric("Mantenimientos Próximos (30 días)", upcoming)

            with col3:
                overdue = stats.get('overdue_maintenance', 0)
                st.metric("Mantenimientos Vencidos", overdue, delta=f"-{overdue}" if overdue > 0 else "0")

            with col4:
                total_providers = len(stats.get('top_providers', []))
                st.metric("Proveedores Activos", total_providers)

            st.divider()

            # Gráficos
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 Equipos por Estado")
                if stats.get('equipment_by_status'):
                    df_status = pd.DataFrame(stats['equipment_by_status'])
                    fig = px.pie(df_status, values='count', names='status',
                                 title="Distribución de Equipos por Estado",
                                 color_discrete_sequence=px.colors.qualitative.Set3)
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("📦 Equipos por Categoría")
                if stats.get('equipment_by_category'):
                    df_category = pd.DataFrame(stats['equipment_by_category'])
                    fig = px.bar(df_category, x='category', y='count',
                                title="Equipos por Categoría",
                                color='count',
                                color_continuous_scale='blues')
                    st.plotly_chart(fig, use_container_width=True)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🔧 Mantenimientos por Tipo")
                if stats.get('maintenance_by_type'):
                    df_maint = pd.DataFrame(stats['maintenance_by_type'])
                    fig = px.bar(df_maint, x='type', y='count',
                                title="Cantidad de Mantenimientos por Tipo",
                                color='total_cost',
                                color_continuous_scale='reds')
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("💰 Costos de Mantenimiento Mensual")
                if stats.get('maintenance_costs_by_month'):
                    df_costs = pd.DataFrame(stats['maintenance_costs_by_month'])
                    fig = px.line(df_costs, x='month', y='total_cost',
                                 title="Tendencia de Costos de Mantenimiento",
                                 markers=True)
                    st.plotly_chart(fig, use_container_width=True)

            # Top Proveedores
            st.subheader("🏆 Top Proveedores")
            if stats.get('top_providers'):
                df_providers = pd.DataFrame(stats['top_providers'])
                st.dataframe(df_providers, use_container_width=True, hide_index=True)

        else:
            st.error("Error al cargar estadísticas")

    except Exception as e:
        st.error(f"Error: {str(e)}")

# ============================================
# GESTIÓN DE EQUIPOS
# ============================================

def equipment_page():
    st.markdown('<h1 class="main-header">💻 Gestión de Equipos</h1>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 Lista de Equipos", "➕ Agregar Equipo"])

    with tab1:
        st.subheader("Inventario de Equipos")

        # Filtros
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            search = st.text_input("🔍 Buscar", placeholder="Nombre, código, marca...")

        with col2:
            try:
                response = api.get_categories()
                if response.status_code == 200:
                    categories = response.json()
                    category_options = {"Todas": None}
                    category_options.update({cat['name']: cat['id'] for cat in categories})
                    selected_category = st.selectbox("Categoría", list(category_options.keys()))
                    category_id = category_options[selected_category]
                else:
                    category_id = None
            except:
                category_id = None

        with col3:
            status = st.selectbox("Estado", ["Todos", "operational", "in_maintenance", "broken", "retired"])
            status_filter = None if status == "Todos" else status

        with col4:
            if st.button("🔄 Actualizar", use_container_width=True):
                st.rerun()

        # Obtener equipos
        try:
            params = {}
            if search:
                params['search'] = search
            if category_id:
                params['category_id'] = category_id
            if status_filter:
                params['status'] = status_filter

            response = api.get_equipment(params)

            if response.status_code == 200:
                equipment_list = response.json()

                if equipment_list:
                    df = pd.DataFrame(equipment_list)

                    # Seleccionar columnas a mostrar
                    display_columns = ['asset_code', 'name', 'brand', 'model', 'status']
                    if 'category' in df.columns:
                        df['category_name'] = df['category'].apply(lambda x: x['name'] if isinstance(x, dict) else '')
                        display_columns.append('category_name')

                    st.dataframe(
                        df[display_columns] if all(col in df.columns for col in display_columns) else df,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.info(f"Total de equipos: {len(equipment_list)}")
                else:
                    st.info("No se encontraron equipos")
            else:
                st.error("Error al cargar equipos")

        except Exception as e:
            st.error(f"Error: {str(e)}")

    with tab2:
        st.subheader("Registrar Nuevo Equipo")

        with st.form("equipment_form"):
            col1, col2 = st.columns(2)

            with col1:
                asset_code = st.text_input("Código de Activo *", help="Código único del equipo")
                name = st.text_input("Nombre del Equipo *")
                brand = st.text_input("Marca")
                model = st.text_input("Modelo")
                serial_number = st.text_input("Número de Serie")

            with col2:
                try:
                    response = api.get_categories()
                    if response.status_code == 200:
                        categories = response.json()
                        category_options = {cat['name']: cat['id'] for cat in categories}
                        selected_cat = st.selectbox("Categoría", list(category_options.keys()))
                        category_id = category_options[selected_cat]
                    else:
                        category_id = None
                except:
                    category_id = None

                purchase_date = st.date_input("Fecha de Compra")
                purchase_price = st.number_input("Precio de Compra", min_value=0.0, step=100.0)
                warranty_months = st.number_input("Garantía (meses)", min_value=0, value=12)

            description = st.text_area("Descripción")
            notes = st.text_area("Notas Adicionales")

            submit = st.form_submit_button("💾 Guardar Equipo", use_container_width=True)

            if submit:
                if asset_code and name:
                    try:
                        data = {
                            "asset_code": asset_code,
                            "name": name,
                            "brand": brand if brand else None,
                            "model": model if model else None,
                            "serial_number": serial_number if serial_number else None,
                            "category_id": category_id,
                            "purchase_date": purchase_date.isoformat() if purchase_date else None,
                            "purchase_price": purchase_price if purchase_price > 0 else None,
                            "warranty_months": warranty_months,
                            "description": description if description else None,
                            "notes": notes if notes else None,
                            "created_by": st.session_state.get('user', {}).get('id')
                        }

                        response = api.create_equipment(data)

                        if response.status_code == 201:
                            st.success("✅ Equipo registrado exitosamente")
                            st.rerun()
                        else:
                            st.error(f"Error al registrar equipo: {response.json().get('detail', 'Error desconocido')}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Por favor, complete los campos obligatorios (*)")

# ============================================
# GESTIÓN DE PROVEEDORES
# ============================================

def providers_page():
    st.markdown('<h1 class="main-header">🏢 Gestión de Proveedores</h1>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 Lista de Proveedores", "➕ Agregar Proveedor"])

    with tab1:
        st.subheader("Proveedores Registrados")

        try:
            response = api.get_providers()

            if response.status_code == 200:
                providers = response.json()

                if providers:
                    df = pd.DataFrame(providers)
                    display_columns = ['name', 'ruc', 'contact_person', 'phone', 'email', 'is_active']

                    st.dataframe(
                        df[display_columns] if all(col in df.columns for col in display_columns) else df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No hay proveedores registrados")
            else:
                st.error("Error al cargar proveedores")

        except Exception as e:
            st.error(f"Error: {str(e)}")

    with tab2:
        st.subheader("Registrar Nuevo Proveedor")

        with st.form("provider_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Nombre del Proveedor *")
                ruc = st.text_input("RUC")
                contact_person = st.text_input("Persona de Contacto")

            with col2:
                phone = st.text_input("Teléfono")
                email = st.text_input("Email")
                website = st.text_input("Sitio Web")

            address = st.text_area("Dirección")

            submit = st.form_submit_button("💾 Guardar Proveedor", use_container_width=True)

            if submit:
                if name:
                    try:
                        data = {
                            "name": name,
                            "ruc": ruc if ruc else None,
                            "contact_person": contact_person if contact_person else None,
                            "phone": phone if phone else None,
                            "email": email if email else None,
                            "website": website if website else None,
                            "address": address if address else None,
                            "created_by": st.session_state.get('user', {}).get('id')
                        }

                        response = api.create_provider(data)

                        if response.status_code == 201:
                            st.success("✅ Proveedor registrado exitosamente")
                            st.rerun()
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Error desconocido')}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("El nombre del proveedor es obligatorio")

# ============================================
# GESTIÓN DE MANTENIMIENTO
# ============================================

def maintenance_page():
    st.markdown('<h1 class="main-header">🔧 Gestión de Mantenimiento</h1>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Todos", "➕ Nuevo", "⏰ Próximos", "🚨 Vencidos"])

    with tab1:
        st.subheader("Historial de Mantenimientos")

        # Filtros
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            filter_status = st.selectbox(
                "Estado",
                ["Todos", "scheduled", "in_progress", "completed", "cancelled"]
            )

        with col2:
            filter_type = st.selectbox(
                "Tipo",
                ["Todos", "preventive", "corrective"]
            )

        with col3:
            filter_equipment = st.number_input("ID Equipo", min_value=0, value=0)

        with col4:
            if st.button("🔄 Actualizar", use_container_width=True):
                st.rerun()

        try:
            params = {}
            if filter_status != "Todos":
                params['status'] = filter_status
            if filter_type != "Todos":
                params['type'] = filter_type
            if filter_equipment > 0:
                params['equipment_id'] = filter_equipment

            response = api.get_maintenance(params)

            if response.status_code == 200:
                maintenance_list = response.json()

                if maintenance_list:
                    # Mostrar cada mantenimiento con opciones de editar/eliminar
                    for maint in maintenance_list:
                        with st.expander(f"🔧 Mantenimiento #{maint['id']} - Equipo {maint['equipment_id']} - {maint['type']} - {maint['status']}"):
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                st.write(f"**Descripción:** {maint['description']}")
                                st.write(f"**Fecha Programada:** {maint.get('scheduled_date', 'N/A')}")
                                st.write(f"**Fecha Realizada:** {maint.get('performed_date', 'N/A')}")
                                st.write(f"**Técnico:** {maint.get('technician', 'N/A')}")
                                st.write(f"**Costo:** ${maint.get('cost', 0)}")
                                if maint.get('diagnosis'):
                                    st.write(f"**Diagnóstico:** {maint['diagnosis']}")
                                if maint.get('solution'):
                                    st.write(f"**Solución:** {maint['solution']}")

                            with col2:
                                if st.button(f"✏️ Editar", key=f"edit_{maint['id']}"):
                                    st.session_state['edit_maintenance_id'] = maint['id']
                                    st.session_state['editing_maintenance'] = True
                                    st.rerun()

                                if st.button(f"🗑️ Eliminar", key=f"delete_{maint['id']}"):
                                    try:
                                        delete_response = api.delete_maintenance(maint['id'])
                                        if delete_response.status_code == 200:
                                            st.success("✅ Mantenimiento eliminado")
                                            st.rerun()
                                        else:
                                            st.error("Error al eliminar")
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")

                    st.info(f"Total de mantenimientos: {len(maintenance_list)}")
                else:
                    st.info("No hay mantenimientos registrados")
            else:
                st.error("Error al cargar mantenimientos")

        except Exception as e:
            st.error(f"Error: {str(e)}")

    with tab2:
        # Verificar si estamos editando o creando
        editing = st.session_state.get('editing_maintenance', False)
        edit_id = st.session_state.get('edit_maintenance_id', None)

        if editing and edit_id:
            st.subheader(f"Editar Mantenimiento #{edit_id}")

            # Obtener datos del mantenimiento
            try:
                response = api.get_maintenance_by_id(edit_id)
                if response.status_code == 200:
                    maint_data = response.json()
                else:
                    st.error("Error al cargar datos del mantenimiento")
                    maint_data = None
            except:
                maint_data = None

            if maint_data:
                with st.form("edit_maintenance_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        scheduled_date = st.date_input(
                            "Fecha Programada",
                            value=datetime.strptime(maint_data['scheduled_date'], '%Y-%m-%d').date() if maint_data.get('scheduled_date') else date.today()
                        )
                        has_performed = st.checkbox(
                            "¿Ya fue realizado?",
                            value=bool(maint_data.get('performed_date'))
                        )
                        if has_performed:
                            performed_date_value = date.today()
                            if maint_data.get('performed_date'):
                                try:
                                    performed_date_value = datetime.strptime(maint_data['performed_date'], '%Y-%m-%d').date()
                                except:
                                    performed_date_value = date.today()
                            performed_date = st.date_input("Fecha Realizada", value=performed_date_value)
                        else:
                            performed_date = None
                        technician = st.text_input("Técnico", value=maint_data.get('technician') or '')
                        cost_value = float(maint_data.get('cost')) if maint_data.get('cost') is not None else 0.0
                        cost = st.number_input("Costo", min_value=0.0, value=cost_value, step=10.0)

                    with col2:
                        status = st.selectbox(
                            "Estado",
                            ["scheduled", "in_progress", "completed", "cancelled"],
                            index=["scheduled", "in_progress", "completed", "cancelled"].index(maint_data['status'])
                        )
                        next_maintenance = st.date_input("Próximo Mantenimiento")

                    description = st.text_area("Descripción", value=maint_data.get('description', ''))
                    diagnosis = st.text_area("Diagnóstico", value=maint_data.get('diagnosis', ''))
                    solution = st.text_area("Solución", value=maint_data.get('solution', ''))

                    col1, col2 = st.columns(2)
                    with col1:
                        submit = st.form_submit_button("💾 Guardar Cambios", use_container_width=True)
                    with col2:
                        cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)

                    if cancel:
                        st.session_state['editing_maintenance'] = False
                        st.session_state['edit_maintenance_id'] = None
                        st.rerun()

                    if submit:
                        try:
                            data = {
                                "scheduled_date": scheduled_date.isoformat() if scheduled_date else None,
                                "performed_date": performed_date.isoformat() if performed_date else None,
                                "technician": technician if technician else None,
                                "description": description,
                                "diagnosis": diagnosis if diagnosis else None,
                                "solution": solution if solution else None,
                                "cost": cost if cost > 0 else None,
                                "status": status,
                                "next_maintenance_date": next_maintenance.isoformat() if next_maintenance else None
                            }

                            update_response = api.update_maintenance(edit_id, data)

                            if update_response.status_code == 200:
                                st.success("✅ Mantenimiento actualizado exitosamente")
                                st.session_state['editing_maintenance'] = False
                                st.session_state['edit_maintenance_id'] = None
                                st.rerun()
                            else:
                                st.error(f"Error: {update_response.json().get('detail', 'Error desconocido')}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        else:
            st.subheader("Registrar Nuevo Mantenimiento")

            # Obtener lista de equipos ANTES del formulario
            equipment_options = {}
            try:
                equip_response = api.get_equipment()
                if equip_response.status_code == 200:
                    equipment_list = equip_response.json()
                    equipment_options = {f"{eq['asset_code']} - {eq['name']}": eq['id'] for eq in equipment_list}
            except:
                pass

            # Obtener proveedores ANTES del formulario
            provider_options = {"Ninguno": None}
            try:
                prov_response = api.get_providers()
                if prov_response.status_code == 200:
                    providers = prov_response.json()
                    provider_options.update({p['name']: p['id'] for p in providers})
            except:
                pass

            if not equipment_options:
                st.warning("⚠️ No hay equipos registrados. Por favor, registre al menos un equipo antes de crear un mantenimiento.")
            else:
                with st.form("maintenance_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        selected_eq = st.selectbox("Equipo *", list(equipment_options.keys()))
                        equipment_id = equipment_options[selected_eq]
                        maintenance_type = st.selectbox("Tipo de Mantenimiento *", ["preventive", "corrective"])
                        scheduled_date = st.date_input("Fecha Programada *")
                        technician = st.text_input("Técnico")

                    with col2:
                        selected_prov = st.selectbox("Proveedor", list(provider_options.keys()))
                        provider_id = provider_options[selected_prov]
                        cost = st.number_input("Costo Estimado", min_value=0.0, step=10.0)
                        status = st.selectbox("Estado", ["scheduled", "in_progress", "completed", "cancelled"])

                    description = st.text_area("Descripción del Mantenimiento *")
                    diagnosis = st.text_area("Diagnóstico (opcional)")
                    solution = st.text_area("Solución Aplicada (opcional)")

                    submit = st.form_submit_button("💾 Registrar Mantenimiento", use_container_width=True)

                    if submit:
                        if equipment_id and description and maintenance_type:
                            try:
                                data = {
                                    "equipment_id": equipment_id,
                                    "type": maintenance_type,
                                    "scheduled_date": scheduled_date.isoformat(),
                                    "technician": technician if technician else None,
                                    "provider_id": provider_id,
                                    "description": description,
                                    "diagnosis": diagnosis if diagnosis else None,
                                    "solution": solution if solution else None,
                                    "cost": cost if cost > 0 else None,
                                    "status": status,
                                    "created_by": st.session_state.get('user', {}).get('id')
                                }

                                response = api.create_maintenance(data)

                                if response.status_code == 201:
                                    st.success("✅ Mantenimiento registrado exitosamente")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {response.json().get('detail', 'Error desconocido')}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                        else:
                            st.warning("Complete los campos obligatorios (*)")

    with tab3:
        st.subheader("Mantenimientos Próximos (30 días)")

        try:
            response = api.get_upcoming_maintenance(30)

            if response.status_code == 200:
                upcoming = response.json()

                if upcoming:
                    for maint in upcoming:
                        with st.container():
                            col1, col2, col3 = st.columns([2, 2, 1])
                            with col1:
                                st.write(f"**Equipo ID:** {maint['equipment_id']}")
                                st.write(f"**Tipo:** {maint['type']}")
                            with col2:
                                st.write(f"**Fecha:** {maint['scheduled_date']}")
                                st.write(f"**Técnico:** {maint.get('technician', 'N/A')}")
                            with col3:
                                if st.button("Ver Detalles", key=f"upcoming_{maint['id']}"):
                                    st.session_state['edit_maintenance_id'] = maint['id']
                                    st.session_state['editing_maintenance'] = True
                                    st.rerun()
                            st.divider()
                    st.info(f"Total: {len(upcoming)} mantenimientos programados")
                else:
                    st.success("✅ No hay mantenimientos programados para los próximos 30 días")
            else:
                st.error("Error al cargar mantenimientos próximos")

        except Exception as e:
            st.error(f"Error: {str(e)}")

    with tab4:
        st.subheader("Mantenimientos Vencidos")

        try:
            response = api.get_overdue_maintenance()

            if response.status_code == 200:
                overdue = response.json()

                if overdue:
                    for maint in overdue:
                        with st.container():
                            col1, col2, col3 = st.columns([2, 2, 1])
                            with col1:
                                st.write(f"**Equipo ID:** {maint['equipment_id']}")
                                st.write(f"**Tipo:** {maint['type']}")
                            with col2:
                                st.write(f"**Fecha Programada:** {maint['scheduled_date']}")
                                st.write(f"**Descripción:** {maint['description'][:50]}...")
                            with col3:
                                if st.button("Actualizar", key=f"overdue_{maint['id']}"):
                                    st.session_state['edit_maintenance_id'] = maint['id']
                                    st.session_state['editing_maintenance'] = True
                                    st.rerun()
                            st.divider()
                    st.warning(f"⚠️ Hay {len(overdue)} mantenimientos vencidos")
                else:
                    st.success("✅ No hay mantenimientos vencidos")
            else:
                st.error("Error al cargar mantenimientos vencidos")

        except Exception as e:
            st.error(f"Error: {str(e)}")

# ============================================
# REPORTES
# ============================================

def reports_page():
    st.markdown('<h1 class="main-header">📄 Reportes</h1>', unsafe_allow_html=True)

    st.subheader("Exportar Reportes")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Reporte de Equipos")

        if st.button("📥 Descargar Excel - Equipos", use_container_width=True):
            try:
                response = api.download_equipment_excel()
                if response.status_code == 200:
                    st.download_button(
                        label="💾 Guardar Archivo Excel",
                        data=response.content,
                        file_name=f"equipos_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error("Error al generar reporte")
            except Exception as e:
                st.error(f"Error: {str(e)}")

        if st.button("📥 Descargar PDF - Equipos", use_container_width=True):
            try:
                response = api.download_equipment_pdf()
                if response.status_code == 200:
                    st.download_button(
                        label="💾 Guardar Archivo PDF",
                        data=response.content,
                        file_name=f"equipos_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Error al generar reporte")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    with col2:
        st.markdown("### 🔧 Reporte de Mantenimientos")

        if st.button("📥 Descargar Excel - Mantenimientos", use_container_width=True):
            try:
                response = api.download_maintenance_excel()
                if response.status_code == 200:
                    st.download_button(
                        label="💾 Guardar Archivo Excel",
                        data=response.content,
                        file_name=f"mantenimientos_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error("Error al generar reporte")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ============================================
# NAVEGACIÓN PRINCIPAL
# ============================================

def main():
    # Verificar si el usuario está autenticado
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login_page()
        return

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=Universidad", use_column_width=True)

        user = st.session_state.get('user', {})
        st.markdown(f"### 👤 {user.get('full_name', 'Usuario')}")
        st.markdown(f"**Rol:** {user.get('role', 'N/A')}")

        st.divider()

        # Menú de navegación
        menu_options = {
            "Dashboard": "📊",
            "Equipos": "💻",
            "Proveedores": "🏢",
            "Mantenimiento": "🔧",
            "Reportes": "📄"
        }

        selected = st.radio(
            "Navegación",
            list(menu_options.keys()),
            format_func=lambda x: f"{menu_options[x]} {x}"
        )

        st.divider()

        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Mostrar página seleccionada
    if selected == "Dashboard":
        dashboard_page()
    elif selected == "Equipos":
        equipment_page()
    elif selected == "Proveedores":
        providers_page()
    elif selected == "Mantenimiento":
        maintenance_page()
    elif selected == "Reportes":
        reports_page()

if __name__ == "__main__":
    main()
