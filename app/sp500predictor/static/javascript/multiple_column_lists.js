//Multiple Column Lists
// Source: https://stackoverflow.com/questions/2347060/html-css-how-to-create-multiple-column-list

// As soon as the document's structure has been loaded:
document.addEventListener( "DOMContentLoaded", function() {
    // For each html elem:
    elems = document.getElementsByTagName("*"); // OL and UL wanted: chose all (*) here and select later.
    for ( var e = 0; e < elems.length; e++ ) {
        // Check if elem is a list (ordered/unordered) and has class name "cols":
        if ( ( elems[e].tagName == "OL" || elems[e].tagName == "UL" ) && elems[e].className.search("cols") > -1 ) {
            // Collect list items and number of columns (from the rel attribute):
            var list = elems[e];
            var listItems = list.getElementsByTagName("LI");
            var Ncols = list.getAttribute("rel")*1; // *1 converts rel from string to int.
            // Determine total number of items, items per column and column width:
            var Ntotal = listItems.length;
            var Npercol = Math.ceil( Ntotal/Ncols );
            var colWidth = Math.floor( 100/Ncols )+"%";
            // For each column:
            for ( var c = 0; c < Ncols; c++ ) {
                // Create column div:
                var colDiv = document.createElement("DIV");
                colDiv.style.cssFloat = "left";
                colDiv.style.width = colWidth;
                // Add list items to column div:
                var i_start = c*Npercol;
                var i_end = Math.min( (c+1)*Npercol, Ntotal );
                for ( var i = i_start; i < i_end; i++ )
                    colDiv.appendChild( listItems[0] ); // Using listItems[0] instead of listItems[i], because items are moved to colDiv!
                // Add column div to list:
                list.appendChild( colDiv );
            }
        }
    }
} );
