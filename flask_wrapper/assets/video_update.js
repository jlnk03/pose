document.addEventListener('DOMContentLoaded', function() {

});

document.addEventListener('DOMContentLoaded', function() {
     let interval = setInterval(function () {
     let navbar = document.getElementById("file_list")
     // console.log(navbar)
     if (navbar) {
         clearInterval(interval);

         const observer = new MutationObserver(function (mutations) {
             // console.log("mutation detected")
             mutations.forEach(function (mutation) {

                 let videoSearcher = setInterval(function () {
                        let video = document.getElementById("video")
                        let sequence = document.getElementsByClassName("js-plotly-plot")[1]
                        let element = document.getElementsByClassName("xtick");
                        if (video && element.length > 0) {
                            clearInterval(videoSearcher)
                                const lineIndex = 0;
                            console.log("video found")
                            console.log(sequence)
                            console.log(video)

                            // Set the initial position of the line
                             Plotly.update(sequence, {
                                  shapes: [
                                    //line vertical
                                    {
                                      type: 'line',
                                      x0: 1,
                                      y0: 0,
                                      x1: 1,
                                      y1: 2,
                                      line: {
                                        color: 'rgb(55, 128, 191)',
                                        width: 3
                                      }
                                    }]
                             })

                            // let interval_vid = setInterval(function () {
                            //             Plotly.update(sequence, {
                            //                 x: [[video.currentTime]],
                            //             }, null, [3]);
                            // }, 100);

                        }
                 }, 100)
             });
         });

         const observerOptions = {
             attributes: true,
             childList: true,
             characterData: true
         };

         observer.observe(navbar, observerOptions);
     }
     }, 100);
 });