import Line
import LastNLines

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video Processing')
    parser.add_argument(
        'source',
        type=str,
        help='Name of the video file to process'
    )
    parser.add_argument(
        'destination',
        type=str,
        nargs='?',
        default='output_video\track1.mp4',
        help='Name and path to the destination video folder'
    )
    args = parser.parse_args()

    dist_pickle = pickle.load( open( "wide_dist_pickle.p", "rb" ) )
    mtx = dist_pickle["mtx"]
    dist = dist_pickle["dist"]

    video = Video(args.source, mtx, dist)
    video.start()