from st_pages import Page, Section, show_pages, add_page_title

add_page_title()

show_pages(
    [
        Section('PROD'),
        Page('src/frontend/pages/investigate_layouts.py',
             'Setup',
             in_section=True),
        Page('src/frontend/pages/dashboard.py',
             'Dashboard',
             in_section=True),

        Section('DEV'),
        Page('src/frontend/pages/detect_activities.py',
             'Detect Activities',
             in_section=True),
        Page('src/frontend/pages/monitor_sensors.py',
             'Monitor Sensors',
             in_section=True),
        Page('src/frontend/pages/propose_stategies.py',
             'Propose Strategies',
             in_section=True),
    ]
)
