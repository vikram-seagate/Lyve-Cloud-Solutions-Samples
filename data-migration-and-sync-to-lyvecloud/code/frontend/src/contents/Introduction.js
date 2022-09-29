import {mainContentHeight} from "../common/style";

const styles = {
    intro: {
        padding: "3rem",
        height: mainContentHeight,
    }, title: {
        textAlign: "center"
    }
};

function Introduction() {
    return <div style={styles.intro}>
        <h1>Introduction Video</h1>
        <iframe width="1120" height="630" src="https://www.youtube.com/embed/k_-nLFwmF9I" title="YouTube video player"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen></iframe>
        {/*<video width="320" height="240" controls>*/}
        {/*    <source src="movie.mp4" type="video/mp4">*/}
        {/*        <source src="movie.ogg" type="video/ogg">*/}
        {/*            Your browser does not support the video tag.*/}
        {/*</video>*/}
    </div>;
}

export default Introduction;