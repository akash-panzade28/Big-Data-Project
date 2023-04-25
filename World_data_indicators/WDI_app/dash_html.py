# This is the base template used by the dash page
index_string = '''

    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
             
            <!-- Primary Meta Tags -->
            <title>{%title%}</title> 
            <title>WORLD INDICATORS</title>
            {%favicon%}
            {%css%}     
            <script async src="https://www.googletagmanager.com/gtag/js?id=SECRET_GA4_TAG"></script> 
            <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'SECRET_GA4_TAG');
            </script>            
            
        </head>

        <style>
            * {
            box-sizing: border-box;
            }

            /* Column css bullshit */
            .column {
            float: left;            
            padding: 30px;            
            }

            .left {
            width: 85%
            }

            .right {
            width: 15%
            }


            body {
            /*overflow-y: hidden; /* Hide vertical scrollbar */
            overflow-x: hidden; /* Hide horizontal scrollbar */
            }

            
        </style>
        
        <body>        
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}           
            </footer>  

            
            
            </body>
    </html>
    '''
    
