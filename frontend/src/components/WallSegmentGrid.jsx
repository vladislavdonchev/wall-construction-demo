import PropTypes from 'prop-types'

/**
 * WallSegmentGrid displays wall sections in a visual grid with color-coded heights
 *
 * @param {Object} props
 * @param {Array} props.profiles - Array of profile objects with sections
 * @returns {JSX.Element}
 */
export default function WallSegmentGrid({ profiles }) {
  if (!profiles || profiles.length === 0) {
    return null
  }

  /**
   * Calculate background color based on height (0-30 feet)
   * White (0) to pastel blue (30)
   */
  const getBackgroundColor = (height) => {
    const opacity = height / 30
    return `rgba(173, 216, 230, ${opacity})`
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold mb-4">Wall Segments</h3>

      {[...profiles].reverse().map((profile, profileIndex) => (
        <div key={profileIndex} className="space-y-2">
          <h4 className="text-md font-medium text-gray-700">{profile.name}</h4>

          <div className="grid grid-flow-col auto-cols-max gap-1">
            {profile.wall_sections && profile.wall_sections.map((section, sectionIndex) => (
              <div
                key={sectionIndex}
                className="flex items-center justify-center w-16 h-16 border border-gray-300 font-bold text-gray-800"
                style={{ backgroundColor: getBackgroundColor(section.initial_height) }}
                title={`${section.section_name}: ${section.initial_height} ft`}
              >
                {section.initial_height}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

WallSegmentGrid.propTypes = {
  profiles: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      wall_sections: PropTypes.arrayOf(
        PropTypes.shape({
          section_name: PropTypes.string.isRequired,
          initial_height: PropTypes.number.isRequired,
        })
      ),
    })
  ),
}
