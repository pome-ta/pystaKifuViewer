
from math import sin, cos, pi
'''
底辺の長さ：1
底辺と高さの比：1.1
頂角の角度：144
底角の角度：81
頂角の座標：[0, 0]
中角(左)の座標: [-0.3434519151136511, 0.11159429192933745]
中角(右)の座標: [0.3434519151136511, 0.11159429192933745]
底角(左)の座標: [-0.5, 1.1]
底角(右)の座標: [0.5, 1.1]

底辺の長さ：45
底辺と高さの比：1.1
頂角の角度：144
底角の角度：81
頂角の座標：[0, 0]
中角(左)
の座標: [-15.455336180114301, 5.021743136820186]
中角(右)
の座標: [15.455336180114301, 5.021743136820186]
底角(左)
の座標: [-22.5, 49.50000000000001]
底角(右)
の座標: [22.5, 49.50000000000001]


頂角の座標	    [0.00, 0.00]
中角(左)の座標	[-103.04, 33.48]
中角(右)の座標	[103.04, 33.48]
底角(左)の座標	[-150.00, 330.00]
底角(右)の座標	[150.00, 330.00]


function App(props) {
    const [bottomLineLength, setBottomLineLength] = useState(300);
    const [aspectRatio, setAspectRatio] = useState(1.1)
    const [topDegree, setTopDegree] = useState(144);
    const [bottomDegree, setBottomDegree] = useState(81);
    const [topCoords, setTopCoords] = useState([0, 0]);
    const [middleLeftCoords, setMiddleLeftCoords] = useState([0, 0]);
    const [middleRightCoords, setMiddleRightCoords] = useState([0, 0]);
    const [bottomLeftCoords, setBottomLeftCoords] = useState([0, 0]);
    const [bottomRightCoords, setBottomRightCoords] = useState([0, 0]);
    const [pieceColor, setPieceColor] = useState("#AD7D45");

    const doChangeAspectRatio = ((event) => {
        setAspectRatio(event.target.value)
    })

    const doChangeTopDegree = ((event) => {
        setTopDegree(event.target.value)
    })

    const doChangeBottomDegree = ((event) => {
        setBottomDegree(event.target.value)
    })

    const doChangePieceColor = ((event) => {
        setPieceColor(event.target.value)
    })

    useEffect(() => {
        const topRadian = topDegree * (Math.PI / 180);
        const bottomRadian = bottomDegree * (Math.PI / 180);
        const a = bottomLineLength * (aspectRatio * Math.cos(bottomRadian) - (Math.sin(bottomRadian) / 2)) / Math.cos(bottomRadian + (topRadian / 2))
        let qX = a * Math.sin(topRadian / 2)
        let qY = a * Math.cos(topRadian / 2)
        qX = Math.round(qX * 100) / 100
        qY = Math.round(qY * 100) / 100
        let rX = bottomLineLength / 2
        let rY = bottomLineLength * aspectRatio
        rY = Math.round(rY * 100) / 100
        setMiddleLeftCoords([-qX, qY])
        setMiddleRightCoords([qX, qY])
        setBottomLeftCoords([-rX, rY])
        setBottomRightCoords([rX, rY])
    }, [bottomLineLength, aspectRatio, topDegree, bottomDegree])

'''
# width = 1
width = 45
height = 45

top_degree = 144
bottom_degree = 81
bottomline_length = 300
aspect_ratio = 1.1

top_radian = top_degree * (pi / 180)
bottom_radian = bottom_degree * (pi / 180)
a = bottomline_length * (
  aspect_ratio * cos(bottom_radian) -
  (sin(bottom_radian) / 2)) / cos(bottom_radian + (top_radian / 2))

qX = a * sin(top_radian / 2)
qY = a * cos(top_radian / 2)
rX = bottomline_length / 2
rY = bottomline_length * aspect_ratio

print(qX, qY, rX, rY)
