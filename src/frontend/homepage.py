from st_pages import Page, Section, show_pages, add_page_title

add_page_title()

show_pages(
    [
        Section('PROD'),
        Section('DEV'),
        Page('src/frontend/pages/detect_activities.py',
             'Detect Activities',
             in_section=True),
        Page('src/frontend/pages/investigate_layouts.py',
             'Investigate Layouts',
             in_section=True),
        Page('src/frontend/pages/monitor_sensors.py',
             'Monitor Sensors',
             in_section=True),
        Page('src/frontend/pages/propose_stategies.py',
             'Propose Strategies',
             in_section=True),
    ]
)
